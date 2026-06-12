# Gestion des Résultats et des Erreurs (Generic Results & Errors)

Ce document explique le fonctionnement du système de retour standardisé de l'application et comment l'utiliser pour gérer à la fois les données de succès et les erreurs de manière type-safe dans les couches **Repository**, **Service**, **Integration** et **API**.

---

## 1. Principes de base

Toutes les réponses internes de l'application héritent d'une classe de base générique : `GenericAppResult[T, U]`.
- **`T`** représente le type de données retourné en cas de **succès** (ex: un modèle Pydantic, un type primitif, `None`, etc.).
- **`U`** représente le type d'erreur retourné en cas d'**échec** (par défaut, `AppError`).

Le système fournit trois classes spécialisées pour chaque couche de l'architecture :
1. **`CrudResult[T, U]`** (couche Repository)
2. **`ServiceResult[T, U]`** (couche Service)
3. **`IntegrationServiceResult[T, U]`** (couche Services Externes/Intégrations)

---

## 2. Utilisation Standard (Erreurs par défaut : `AppError`)

Dans la majorité des cas, l'erreur par défaut `AppError` est suffisante. Grâce aux types génériques avec valeur par défaut, vous n'avez pas besoin de spécifier le deuxième paramètre de type si vous utilisez `AppError`.

### Exemple dans un Repository :
```python
from app.repositories import CrudResult
from app.schemas.users import UserResponse  # Modèle Pydantic

def get_user_by_id(user_id: int) -> CrudResult[UserResponse]:
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        # L'erreur par défaut est AppError
        error = AppError(
            error_type=AppErrorType.NOT_FOUND,
            error_message="L'utilisateur n'existe pas."
        )
        return CrudResult.crud_failure(error, status_code=404)
        
    return CrudResult.crud_success(UserResponse.model_validate(user))
```

### Exemple dans un Service (Propagation et Conversion) :
```python
from app.services import ServiceResult
from app.repositories import UserRepository

def get_user_profile(user_id: int) -> ServiceResult[UserResponse]:
    # Appel au repository
    repo_res = UserRepository.get_user_by_id(user_id)
    
    if repo_res.is_error():
        # Conversion directe du CrudResult d'erreur en ServiceResult d'erreur.
        # Le type d'erreur (AppError) et le code de statut (404) sont conservés.
        return repo_res.to_service_error(service_name="UserService")
        
    return ServiceResult.service_success(repo_res.data)
```

---

## 3. Utilisation Avancée (Erreurs Personnalisées)

Si une opération nécessite une structure d'erreur spécifique (ex: des erreurs de validation complexes, des détails spécifiques à un service tiers), vous pouvez définir un modèle d'erreur personnalisé et le passer en deuxième paramètre générique.

### Étape 1 : Définir le modèle d'erreur personnalisé
```python
from pydantic import BaseModel

class PaymentErrorDetail(BaseModel):
    transaction_id: str
    failure_code: str
    user_message: str
```

### Étape 2 : Spécifier le type d'erreur dans le Result
```python
from app.services import ServiceResult

def process_payment(amount: float) -> ServiceResult[PaymentResponse, PaymentErrorDetail]:
    payment_status, details = stripe_client.charge(amount)
    
    if not payment_status:
        custom_err = PaymentErrorDetail(
            transaction_id=details.id,
            failure_code=details.code,
            user_message="Votre solde est insuffisant."
        )
        return ServiceResult.service_failure(custom_err, status_code=402)
        
    return ServiceResult.service_success(PaymentResponse(status="success"))
```

---

## 4. Intégration API & Génération OpenAPI / Swagger

Pour que FastAPI génère correctement la documentation interactive (Swagger UI) et valide la réponse HTTP, vous devez configurer le retour de votre route.

### Approche A : Spécification Générique Directe
Vous pouvez annoter directement votre route avec `ApiBaseResponse[DataType, ErrorType]` :

```python
from fastapi import APIRouter, Response
from app.schemas.globals.api_base_response import ApiBaseResponse

router = APIRouter()

@router.post("/pay")
async def pay(response: Response) -> ApiBaseResponse[PaymentResponse, PaymentErrorDetail]:
    service_res = payment_service.process_payment(100.0)
    
    # to_HTTP_api_base_response se charge d'instancier correctement le schéma de réponse
    # et de modifier le status_code HTTP de l'objet Response
    return service_res.to_HTTP_api_base_response(response)
```

### Approche B : Par Sous-classage (Recommandé pour Swagger plus propre)
L'utilisation directe de types génériques imbriqués peut parfois donner des noms de schémas générés automatiquement peu lisibles dans Swagger (ex: `ApiBaseResponse_PaymentResponse_PaymentErrorDetail_`). 

Pour un rendu Swagger premium et des schémas explicites, créez une sous-classe concrète :

```python
# app/schemas/payment.py
from app.schemas.globals.api_base_response import ApiBaseResponse

class PaymentApiResponse(ApiBaseResponse[PaymentResponse, PaymentErrorDetail]):
    """Réponse standardisée pour les opérations de paiement"""
    # Pas besoin de redéclarer les champs, ils sont hérités et typés automatiquement !
```

Puis dans votre routeur :
```python
@router.post("/pay")
async def pay(response: Response) -> PaymentApiResponse:
    service_res = payment_service.process_payment(100.0)
    
    # Le retour est converti et validé proprement
    return service_res.to_HTTP_api_base_response(response)
```

---

## 5. Bonnes Pratiques & Anti-patterns

> [!TIP]
> - **Utilisez toujours les helpers de classe** (`crud_success`, `service_failure`, etc.) au lieu d'instancier les classes directement via `__init__`.
> - **Utilisez l'approche par sous-classage de `ApiBaseResponse`** pour toutes les routes publiques afin de garder votre documentation Swagger claire et professionnelle.

> [!WARNING]
> - **Ne pas court-circuiter le typage** en utilisant `Any` comme type d'erreur si vous connaissez la structure de l'erreur. Spécifier la structure permet au frontend d'avoir un typage rigoureux généré via OpenAPI.
