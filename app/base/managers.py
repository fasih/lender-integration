from django_extensions.db.models import ActivatorModelManager, ActivatorQuerySet



class MFQuerySet(ActivatorQuerySet):
    """
    ActivatorQuerySet

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
        queryset = MFQuerySet(model=self.model, using=self._db)
        return queryset

    def one(self):
        """
        Return latest active instance of ActivatorModel:

        SomeModel.objects.one(), proxy to ActivatorQuerySet.one
        """
        return self.get_queryset().one()
