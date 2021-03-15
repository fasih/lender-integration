from django_extensions.db.models import ActivatorModelManager, ActivatorQuerySet



class ActiveOneQuerySet(ActivatorQuerySet):
    """
    ActiveOneQuerySet

    Queryset that returns statused one result
    """

    def one(self):
        """ Return latest active model object """
        try:
            return self.active().latest('modified')
        except:
            return self.active().last()



class MFModelManager(ActivatorModelManager):

    def get_queryset(self):
        queryset = ActiveOneQuerySet(model=self.model, using=self._db)
        return queryset

    def one(self):
        """
        Return latest active instance of ActivatorModel:

        SomeModel.objects.one(), proxy to ActiveOneQuerySet.one
        """
        return self.get_queryset().one()
