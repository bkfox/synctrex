# TODO
# - doc
# - unregister

class Register:
    """
    Register class that can be re-used to store and retrieve either
    instances of a specific class.

    Since it aims to be also used as metaclass, it should be subclassed.

    TODO note on back ref // item._register = x | []
    """
    items = {}
    key = ''
    """
    Use this attribute on item as key attribute
    """
    back_reference = False
    """
    Add an back reference to registry on items.
    """
    # put there because it is more a question of design than
    # usage.
    unique_register = True
    """
    If True item can be registered only once. Need :py:attr:back_reference
    to be True.
    """

    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)
        self.items = self.items or {}

    def _back_reference(self, item):
        if self.unique_register:
            if hasattr(item._register) and item._register:
                raise ValueError('item is yet register elsewhere')
            item._register = self
            return

        if not hasattr(item._register):
            item._register = [self]
        else:
            item._register.append(self)

    def register(self, item, key = None, overwrite = False):
        """
        Add an item to the register. If Register is configured for,
        back references it to the item.

        :param item: item to register.
        :param key: force to use this key instead of item's key attr.
        :param overwrite: erase existing item if present instead of \
                    raising an exception.
        """
        key = key or getattr(item, self.key)
        if overwrite and key in self.items:
            raise ValueError(
                'There is yet an item "{}" in this registry.'
                .format(key)
            )

        if self.back_reference:
            self._back_reference(item)
        self.items[key] = item

    def get(self, key, default = None):
        """
        Return an item by its key.
        """
        return self.items.get(key, default)

    def filter(self, pred = None, **kwargs):
        """
        Filter in items that matches predicate or given subset
        of values. Yield over those values.

        :params pred: use this predicate function
        :params **kwargs: if pred is None, match item.__dict__ with it
        """
        if pred:
            for key, item in self.items.items():
                if pred and pred(item):
                    yield item
        else:
            for key, item in self.items.items():
                if kwargs.items() <= item.__dict__.items():
                    yield item

