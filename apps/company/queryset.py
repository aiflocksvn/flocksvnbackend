from django.db import models
from django.db.models import QuerySet, Count, Q


class CompanyQuerySet(QuerySet):
    def company_summery_aggregate(self):
        from apps.company.models import Company
        return self.aggregate(
            total=Count('id'),
            approved=Count('id', filter=Q(status=Company.APPROVED)),
            rejected=Count('id', filter=Q(status=Company.REJECTED)),
            pending=Count('id', filter=Q(status=Company.PENDING))
        )


class CompanyManager(models.Manager):
    def get_queryset(self):
        return CompanyQuerySet(self.model, using=self._db)

    def company_summery_aggregate(self):
        return self.get_queryset().company_summery_aggregate()
