from django.db import transaction
from django.db.models.signals import post_delete, pre_save
from django.dispatch import receiver

from apps.schools.models import SchoolDocument


def _delete_file_on_commit(storage, name: str) -> None:
    if name:
        transaction.on_commit(lambda: storage.delete(name))


@receiver(post_delete, sender=SchoolDocument, dispatch_uid="schools_document_file_cleanup")
def delete_document_file(sender, instance: SchoolDocument, **kwargs) -> None:
    _delete_file_on_commit(instance.file.storage, instance.file.name)


@receiver(pre_save, sender=SchoolDocument, dispatch_uid="schools_document_file_replace")
def delete_replaced_document_file(sender, instance: SchoolDocument, **kwargs) -> None:
    if not instance.pk:
        return
    previous_name = (
        SchoolDocument.objects.filter(pk=instance.pk).values_list("file", flat=True).first()
    )
    if previous_name and previous_name != instance.file.name:
        _delete_file_on_commit(instance.file.storage, previous_name)
