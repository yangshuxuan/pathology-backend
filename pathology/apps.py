from django.apps import AppConfig


class PathologyConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'pathology'
    verbose_name = "辅助诊断信息管理"
    def ready(self) -> None:
        import pathology.signals
