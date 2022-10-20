from django.db import models
from django.db.models import QuerySet, Count, Q


class InvestorQuerySet(QuerySet):
    def investor_summery_aggregate(self):
        from apps.investment.models import InvestmentProfile
        return self.aggregate(
            total=Count('id'),
            approved=Count('id', filter=Q(status=InvestmentProfile.APPROVED)),
            rejected=Count('id', filter=Q(status=InvestmentProfile.REJECTED)),
            pending=Count('id', filter=Q(status=InvestmentProfile.PENDING))
        )


class InvestorManager(models.Manager):
    def get_queryset(self):
        return InvestorQuerySet(self.model, using=self._db)

    def investor_summery_aggregate(self):
        return self.get_queryset().investor_summery_aggregate()
