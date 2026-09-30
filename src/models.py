from pydantic import BaseModel, ConfigDict, Field


class UserCredentials(BaseModel):
    """Schema de validation pour les identifiants utilisateur (route /login)."""

    username: str
    password: str


class AdmissionInput(BaseModel):
    """Schema de validation pour les donnees d'admission d'un etudiant (route /predict).

    Supporte a la fois les noms snake_case (gre_score) et les noms avec espaces (GRE Score).
    """

    model_config = ConfigDict(populate_by_name=True)

    gre_score: float = Field(
        ...,
        alias="GRE Score",
        ge=0,
        le=340,
        description="Score GRE sur 340",
    )
    toefl_score: float = Field(
        ...,
        alias="TOEFL Score",
        ge=0,
        le=120,
        description="Score TOEFL sur 120",
    )
    university_rating: float = Field(
        ...,
        alias="University Rating",
        ge=1,
        le=5,
        description="Classement universite sur 5",
    )
    sop: float = Field(
        ...,
        alias="SOP",
        ge=1.0,
        le=5.0,
        description="Statement of Purpose sur 5",
    )
    lor: float = Field(
        ...,
        alias="LOR",
        ge=1.0,
        le=5.0,
        description="Letter of Recommendation sur 5",
    )
    cgpa: float = Field(
        ...,
        alias="CGPA",
        ge=0.0,
        le=10.0,
        description="Cumulative GPA sur 10",
    )
    research: int = Field(
        ...,
        alias="Research",
        ge=0,
        le=1,
        description="Experience de recherche (0 ou 1)",
    )
