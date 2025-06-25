"""Data classes for Yago."""


class Item:
    def __init__(self, item_id: str, item_label: str, item_description: str, count: int = 0):
        """Instantiate the item.

        Args:
        - item_id: ID of the item
        - item_label: label/alias of the item
        - item_description: description of the item
        - count: count of the item
        """
        self.item_id: str = item_id
        self.item_label: str = item_label
        self.item_description: str = item_description
        self.count: int = count

    def __str__(self) -> str:
        return f'Item: {self.item_id}. {self.item_description} ({self.count})'


class Property:
    def __init__(self, property_id: str, property_label: str, count: int = 0):
        """Instantiate the property.

        Args:
        - property_id: ID of the property
        - property_label: label/alias of the property
        - count: count of the property
        """
        self.property_id: str = property_id
        self.property_label: str = property_label
        self.count: int = count

    def __str__(self) -> str:
        return f'Property: {self.property_id}. {self.property_label} ({self.count})'


class Claim:
    def __init__(self, claim_id: int, subject_id: str, property_id: str, target_id: str):
        """Instantiate the claim.

        Args:
        - claim_id: ID of the claim in the database
        - subject: ID of the subject `Item` of the claim
        - property: ID of the `Property` of the claim
        - target: ID of the target `Item` of the claim
        """
        self.claim_id: int = claim_id
        self.subject_id: str = subject_id
        self.property_id: str = property_id
        self.target_id: str = target_id

    def __str__(self) -> str:
        return f'subject: {self.subject_id}, Property: {self.property_id}, Target: {self.target_id}'