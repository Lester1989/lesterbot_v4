""" This module contains the database models for the charactersheet game. """
import datetime
from functools import lru_cache
import re
from enum import Enum

from sqlalchemy import Boolean, DateTime
from sqlalchemy import Enum as EnumDB
from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.library.db_models import Base, Session


class CategoryUser(Base):
    """
    A class representing a user in the category game.

    A user can be in many categories and a category can have many users. But in each category a user is either a GM or not.
    """

    __tablename__ = "category_users"
    category_id: Mapped[str] = mapped_column(String, primary_key=True)
    user_id: Mapped[str] = mapped_column(String, primary_key=True)
    is_gm: Mapped[bool] = mapped_column(Boolean, default=False)

    @staticmethod
    def get(category_id: str, user_id: str) -> "CategoryUser":
        """ Get a category user by category and user ids (ints). """
        with Session() as session:
            return (
                session.query(CategoryUser)
                .filter(CategoryUser.category_id == category_id, CategoryUser.user_id == user_id)
                .first()
            )

    @staticmethod
    def get_by_category(category_id: str) -> list["CategoryUser"]:
        """ Get all category users for a category. """
        with Session() as session:
            return session.query(CategoryUser).filter(CategoryUser.category_id == category_id).all()

    @staticmethod
    def get_by_user(user_id: str) -> list["CategoryUser"]:
        """ Get all category users for a user. """
        with Session() as session:
            return session.query(CategoryUser).filter(CategoryUser.user_id == user_id).all()

    @staticmethod
    def create(category_id: str, user_id: str, is_gm: bool = False) -> "CategoryUser":
        """ Create a new category user. """
        with Session() as session:
            category_user = CategoryUser(category_id=category_id, user_id=user_id, is_gm=is_gm)
            session.add(category_user)
            session.commit()
            return category_user

    @staticmethod
    def delete(category_id: str, user_id: str) -> int:
        """ Delete a category user and return the number of deleted rows. """
        with Session() as session:
            result = session.query(CategoryUser).filter(
                CategoryUser.category_id == category_id, CategoryUser.user_id == user_id
            ).delete()
            session.commit()
            return result

    @staticmethod
    def update(category_id: str, user_id: str, is_gm: bool) -> "CategoryUser":
        """ Set the GM status of a user in a category. """
        with Session() as session:
            category_user = (
                session.query(CategoryUser)
                .filter(CategoryUser.category_id == category_id, CategoryUser.user_id == user_id)
                .first()
            )
            category_user.is_gm = is_gm
            session.commit()
            return category_user


class GroupState(Enum):
    """An enum representing the state of a group."""

    CREATING = "creating"
    STARTED = "started"


class CategorySetting(Base):
    """ A class representing a setting in the category game. """

    __tablename__ = "category_settings"
    category_id: Mapped[str] = mapped_column(String, primary_key=True)
    state: Mapped[GroupState] = mapped_column(EnumDB(GroupState), default=GroupState.CREATING)
    rule_system: Mapped[str] = mapped_column(String, default="")
    changes_need_approval: Mapped[bool] = mapped_column(Boolean, default=True)
    character_hidden: Mapped[bool] = mapped_column(Boolean, default=True)
    hidden_rolls_allowed: Mapped[bool] = mapped_column(Boolean, default=True)
    web_interface_enabled: Mapped[bool] = mapped_column(Boolean, default=True)

    @staticmethod
    def get_by_category(category_id: str) -> "CategorySetting":
        """ Get the settings for a category. """
        with Session() as session:
            return (
                session.query(CategorySetting)
                .filter(CategorySetting.category_id == category_id)
                .first()
            )

    @staticmethod
    def create(category_id: str) -> "CategorySetting":
        """ Create a new category setting with default values. """
        with Session() as session:
            category_setting = CategorySetting(category_id=category_id)
            session.add(category_setting)
            session.commit()
            return category_setting

    @staticmethod
    def delete(category_id: str) -> None:
        """ Delete a category setting. """
        with Session() as session:
            session.query(CategorySetting).filter(
                CategorySetting.category_id == category_id
            ).delete()
            session.commit()

    @staticmethod
    def update(
        category_id: str,
        state: GroupState = None,
        rule_system: str = None,
        changes_need_approval: bool = None,
        character_hidden: bool = None,
        hidden_rolls_allowed: bool = None,
        web_interface_enabled: bool = None,
    ) -> "CategorySetting":
        """ Update a category setting. If a parameter is None, it will not be updated. """
        with Session() as session:
            category_setting = (
                session.query(CategorySetting)
                .filter(CategorySetting.category_id == category_id)
                .first()
            )
            if state is not None:
                category_setting.state = state
            if rule_system is not None:
                category_setting.rule_system = rule_system
            if changes_need_approval is not None:
                category_setting.changes_need_approval = changes_need_approval
            if character_hidden is not None:
                category_setting.character_hidden = character_hidden
            if hidden_rolls_allowed is not None:
                category_setting.hidden_rolls_allowed = hidden_rolls_allowed
            if web_interface_enabled is not None:
                category_setting.web_interface_enabled = web_interface_enabled
            session.commit()
            return category_setting


class CharacterHeader(Base):
    """ A class representing the header in a charactersheet. """

    __tablename__ = "character_headers"
    user_id: Mapped[str] = mapped_column(String, primary_key=True)
    category_id: Mapped[str] = mapped_column(String, primary_key=True)
    name: Mapped[str] = mapped_column(String, primary_key=True)
    concept: Mapped[str] = mapped_column(String)
    description: Mapped[str] = mapped_column(String)
    image_url: Mapped[str] = mapped_column(String)
    is_inactive: Mapped[bool] = mapped_column(Boolean, default=False)

    @staticmethod
    def create(
        user_id: str,
        category_id: str,
        name: str,
        concept: str,
        description: str = "",
        image_url: str = "",
    ) -> "CharacterHeader":
        """ Create a new character header. """
        with Session() as session:
            character_header = CharacterHeader(
                user_id=user_id,
                category_id=category_id,
                name=name,
                concept=concept,
                description=description,
                image_url=image_url,
            )
            session.add(character_header)
            session.commit()
            return character_header

    @staticmethod
    def get(user_id: str, category_id: str, name: str) -> "CharacterHeader":
        """ Get a character header by user, category, and name. """
        with Session() as session:
            return (
                session.query(CharacterHeader)
                .filter(
                    CharacterHeader.user_id == user_id,
                    CharacterHeader.category_id == category_id,
                    CharacterHeader.name == name,
                )
                .first()
            )

    @staticmethod
    def get_available(user_id: str, category_id: str) -> list["CharacterHeader"]:
        """ Get all available character headers for a user in a category. """
        with Session() as session:
            return (
                session.query(CharacterHeader)
                .filter(
                    CharacterHeader.user_id == user_id, CharacterHeader.category_id == category_id
                )
                .all()
            )

    @staticmethod
    def find_by_name(category_id: str, name: str) -> list["CharacterHeader"]:
        """ Find all character headers by name in a category. """
        with Session() as session:
            return (
                session.query(CharacterHeader)
                .filter(
                    CharacterHeader.category_id == category_id,
                    CharacterHeader.name.ilike(f"%{name}%"),
                )
                .all()
            )

    @staticmethod
    def get_by_category(category_id: str) -> dict[tuple[str, str], list["CharacterHeader"]]:
        """ Get all character headers for a category grouped by user_id and character name."""
        with Session() as session:
            raw_result = (
                session.query(CharacterHeader)
                .filter(CharacterHeader.category_id == category_id)
                .all()
            )

        grouped_result: dict[tuple[str, str], list[CharacterHeader]] = {}
        for entry in raw_result:
            sheet_id = (entry.user_id, entry.name)
            if sheet_id not in grouped_result:
                grouped_result[sheet_id] = []
            grouped_result[sheet_id].append(entry)
        return grouped_result

    @staticmethod
    def delete(user_id: str, category_id: str, name: str) -> None:
        """ Delete a character header by user, category, and name. """
        with Session() as session:
            session.query(CharacterHeader).filter(
                CharacterHeader.user_id == user_id,
                CharacterHeader.category_id == category_id,
                CharacterHeader.name == name,
            ).delete()
            session.commit()

    @staticmethod
    def update(
        user_id: str,
        category_id: str,
        name: str,
        concept: str = None,
        description: str = None,
        image_url: str = None,
        is_inactive: bool = None,
    ) -> "CharacterHeader":
        """ Update a character header identified by user, category, and name. """
        with Session() as session:
            character_header = (
                session.query(CharacterHeader)
                .filter(
                    CharacterHeader.user_id == user_id,
                    CharacterHeader.category_id == category_id,
                    CharacterHeader.name == name,
                )
                .first()
            )
            if concept is not None:
                character_header.concept = concept
            if description is not None:
                character_header.description = description
            if image_url is not None:
                character_header.image_url = image_url
            if is_inactive is not None:
                character_header.is_inactive = is_inactive
            session.commit()
            return character_header


class AttributeType(Enum):
    """An enum representing the type of an attribute for grouping of character values."""

    ATTRIBUTE = "attribute"
    SKILL = "skill"
    SPECIALTY = "specialty"
    GENERAL = "general"
    UNKNOWN = "unknown"


class CharactersheetEntry(Base):
    """ A class representing an entry in a charactersheet. """

    __tablename__ = "charactersheet_entries"
    user_id: Mapped[str] = mapped_column(String, primary_key=True)
    category_id: Mapped[str] = mapped_column(String, primary_key=True)
    name: Mapped[str] = mapped_column(String, primary_key=True)
    sheet_key: Mapped[str] = mapped_column(String, primary_key=True)
    value: Mapped[int] = mapped_column(Integer)
    attribute_type: Mapped[AttributeType] = mapped_column(
        EnumDB(AttributeType), default=AttributeType.ATTRIBUTE
    )

    @staticmethod
    def get(user_id: str, category_id: str, name: str) -> list["CharactersheetEntry"]:
        """ Get a charactersheet entry. """
        with Session() as session:
            return (
                session.query(CharactersheetEntry)
                .filter(
                    CharactersheetEntry.user_id == user_id,
                    CharactersheetEntry.category_id == category_id,
                    CharactersheetEntry.name == name,
                )
                .all()
            )

    @staticmethod
    def get_by_category(category_id: str) -> dict[tuple[int, str], list["CharactersheetEntry"]]:
        """ Get all charactersheet entries for a category grouped by user_id and character name. """
        with Session() as session:
            raw_result = (
                session.query(CharactersheetEntry)
                .filter(CharactersheetEntry.category_id == category_id)
                .all()
            )
        grouped_result: dict[tuple[int, str], list[CharactersheetEntry]] = {}
        for entry in raw_result:
            sheet_id = (entry.user_id, entry.name)
            if sheet_id not in grouped_result:
                grouped_result[sheet_id] = []
            grouped_result[sheet_id].append(entry)
        return grouped_result

    @staticmethod
    def get_by_user(user_id: str) -> dict[tuple[int, str], list["CharactersheetEntry"]]:
        """
        Get all charactersheet entries for a user grouped by category_id and character name.
        """
        with Session() as session:
            raw_result = (
                session.query(CharactersheetEntry)
                .filter(CharactersheetEntry.user_id == user_id)
                .all()
            )
        grouped_result: dict[tuple[int, str], list[CharactersheetEntry]] = {}
        for entry in raw_result:
            sheet_id = (entry.category_id, entry.name)
            if sheet_id not in grouped_result:
                grouped_result[sheet_id] = []
            grouped_result[sheet_id].append(entry)
        return grouped_result

    @staticmethod
    def get_by_user_and_category(user_id: str, category_id: str) -> list["CharactersheetEntry"]:
        """ Get all charactersheet entries for a user in a category. """
        with Session() as session:
            return (
                session.query(CharactersheetEntry)
                .filter(
                    CharactersheetEntry.user_id == user_id,
                    CharactersheetEntry.category_id == category_id,
                )
                .all()
            )

    @staticmethod
    def create(
        user_id: str,
        category_id: str,
        name: str,
        sheet_key: str,
        value: int,
        attribute_type: AttributeType = AttributeType.UNKNOWN,
    ) -> "CharactersheetEntry":
        """ Create a new charactersheet entry. """
        with Session() as session:
            charactersheet_entry = CharactersheetEntry(
                user_id=user_id,
                category_id=category_id,
                name=name,
                sheet_key=sheet_key,
                value=value,
                attribute_type=attribute_type,
            )
            session.add(charactersheet_entry)
            session.commit()
            return charactersheet_entry

    @staticmethod
    def delete(user_id: str, category_id: str, name: str) -> None:
        """ Delete a charactersheet entry. """
        with Session() as session:
            session.query(CharactersheetEntry).filter(
                CharactersheetEntry.user_id == user_id,
                CharactersheetEntry.category_id == category_id,
                CharactersheetEntry.name == name,
            ).delete()
            session.commit()

    @staticmethod
    def remove_key(user_id: str, category_id: str, name: str, sheet_key: str) -> None:
        """ Remove the key of a charactersheet entry. """
        with Session() as session:
            session.query(CharactersheetEntry).filter(
                CharactersheetEntry.user_id == user_id,
                CharactersheetEntry.category_id == category_id,
                CharactersheetEntry.name == name,
                CharactersheetEntry.sheet_key == sheet_key,
            ).delete()
            session.commit()

    @staticmethod
    def update(
        user_id: str,
        category_id: str,
        name: str,
        sheet_key: str,
        value: int = None,
        attribute_type: AttributeType = None,
    ) -> "CharactersheetEntry":
        """ Update a charactersheet entry. """
        with Session() as session:
            charactersheet_entry = (
                session.query(CharactersheetEntry)
                .filter(
                    CharactersheetEntry.user_id == user_id,
                    CharactersheetEntry.category_id == category_id,
                    CharactersheetEntry.name == name,
                    CharactersheetEntry.sheet_key == sheet_key,
                )
                .first()
            )
            if not charactersheet_entry:
                charactersheet_entry = CharactersheetEntry(
                    user_id=user_id,
                    category_id=category_id,
                    name=name,
                    sheet_key=sheet_key,
                    value=value,
                    attribute_type=attribute_type,
                )
                session.add(charactersheet_entry)
            if value is not None:
                charactersheet_entry.value = value
            if attribute_type is not None:
                charactersheet_entry.attribute_type = attribute_type
            session.commit()
            return charactersheet_entry


class ModificationState(Enum):
    """An enum representing the state of a modification."""

    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


class SheetModification(Base):
    """
    A class representing a modification to a charactersheet.

    This can be a new entry, a change to an existing entry, or a deletion. And has a status of pending, approved, or rejected to be managed by the GM.
    """

    __tablename__ = "sheet_modifications"
    user_id: Mapped[str] = mapped_column(String, primary_key=True)
    category_id: Mapped[str] = mapped_column(String, primary_key=True)
    name: Mapped[str] = mapped_column(String, primary_key=True)
    sheet_key: Mapped[str] = mapped_column(String, primary_key=True)
    value: Mapped[int] = mapped_column(Integer)
    attribute_type: Mapped[AttributeType] = mapped_column(
        EnumDB(AttributeType), default=AttributeType.UNKNOWN
    )
    status: Mapped[ModificationState] = mapped_column(
        EnumDB(ModificationState), default=ModificationState.PENDING
    )
    comment: Mapped[str] = mapped_column(String, default="")
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime, default=datetime.datetime.utcnow
    )

    @staticmethod
    def get_key(user_id: str, category_id: str, name: str, sheet_key: str) -> "SheetModification":
        """ Get a sheet modification by key. """
        with Session() as session:
            return (
                session.query(SheetModification)
                .filter(
                    SheetModification.user_id == user_id,
                    SheetModification.category_id == category_id,
                    SheetModification.name == name,
                    SheetModification.sheet_key == sheet_key,
                )
                .first()
            )

    @staticmethod
    def get(user_id: str, category_id: str, name: str) -> list["SheetModification"]:
        """ Get a sheet modification. """
        with Session() as session:
            return (
                session.query(SheetModification)
                .filter(
                    SheetModification.user_id == user_id,
                    SheetModification.category_id == category_id,
                    SheetModification.name == name,
                )
                .all()
            )

    @staticmethod
    def get_by_category(category_id: str) -> dict[tuple[int, str], list["SheetModification"]]:
        """
        Get all sheet modifications for a category.

        Parameters:
        -----------
        category_id : int
            The unique identifier of the category.

        Returns:
        --------
        dict[tuple[int,str],list[SheetModification]]
            A dictionary mapping the user and name to a list of sheet modifications for the category.
        """
        with Session() as session:
            raw_result = (
                session.query(SheetModification)
                .filter(SheetModification.category_id == category_id)
                .all()
            )
        grouped_result: dict[tuple[int, str], list[SheetModification]] = {}
        for entry in raw_result:
            sheet_id = (entry.user_id, entry.name)
            if sheet_id not in grouped_result:
                grouped_result[sheet_id] = []
            grouped_result[sheet_id].append(entry)
        return grouped_result

    @staticmethod
    def get_by_user(user_id: str) -> dict[tuple[int, str], list["SheetModification"]]:
        """
        Get all sheet modifications for a user.

        Parameters:
        -----------
        user_id : int
            The unique identifier of the user.

        Returns:
        --------
        dict[tuple[int,str],list[SheetModification]]
            A dictionary mapping the category and name to a list of sheet modifications for the user.
        """
        with Session() as session:
            raw_result = (
                session.query(SheetModification).filter(SheetModification.user_id == user_id).all()
            )
        grouped_result: dict[tuple[int, str], list[SheetModification]] = {}
        for entry in raw_result:
            sheet_id = (entry.category_id, entry.name)
            if sheet_id not in grouped_result:
                grouped_result[sheet_id] = []
            grouped_result[sheet_id].append(entry)
        return grouped_result

    @staticmethod
    def get_by_user_and_category(user_id: str, category_id: str) -> list["SheetModification"]:
        """
        Get all sheet modifications for a user in a category.

        Parameters:
        -----------
        user_id : int
            The unique identifier of the user.
        category_id : int
            The unique identifier of the category.

        Returns:
        --------
        list[SheetModification]
            A list of all sheet modifications for the user in the category.
        """
        with Session() as session:
            return (
                session.query(SheetModification)
                .filter(
                    SheetModification.user_id == user_id,
                    SheetModification.category_id == category_id,
                )
                .all()
            )

    @staticmethod
    def create(
        user_id: str,
        category_id: str,
        name: str,
        sheet_key: str,
        value: int,
        attribute_type: AttributeType,
        comment: str,
    ) -> "SheetModification":
        """
        Create a new sheet modification.

        Parameters:
        -----------
        user_id : int
            The unique identifier of the user.
        category_id : int
            The unique identifier of the category.
        name : str
            The unique name of the entry in this category for this user.
        sheet_key : str
            The key of the entry.
        value : int
            The value of the entry.
        comment : str
            The comment of the modification.

        Returns:
        --------
        SheetModification
            The created sheet modification.
        """
        with Session() as session:
            sheet_modification = SheetModification(
                user_id=user_id,
                category_id=category_id,
                name=name,
                sheet_key=sheet_key,
                value=value,
                comment=comment,
                attribute_type=attribute_type,
            )
            session.add(sheet_modification)
            session.commit()
            return sheet_modification

    @staticmethod
    def delete(user_id: str, category_id: str, name: str) -> None:
        """
        Delete a sheet modification.

        Parameters:
        -----------
        user_id : int
            The unique identifier of the user.
        category_id : int
            The unique identifier of the category.
        name : str
            The unique name of the entry in this category for this user.
        """
        with Session() as session:
            session.query(SheetModification).filter(
                SheetModification.user_id == user_id,
                SheetModification.category_id == category_id,
                SheetModification.name == name,
            ).delete()
            session.commit()

    @staticmethod
    def update(
        user_id: str,
        category_id: str,
        name: str,
        sheet_key: str,
        value: int = None,
        attribute_type: AttributeType = None,
        status: ModificationState = None,
        comment: str = None,
    ) -> "SheetModification":
        """
        Update a sheet modification.

        Parameters:
        -----------
        user_id : int
            The unique identifier of the user.
        category_id : int
            The unique identifier of the category.
        name : str
            The unique name of the entry in this category for this user.
        sheet_key : str
            The key of the entry.
        value : int
            The value of the entry.
        attribute_type : AttributeType
            The type of the attribute.
        status : ModificationState
            The status of the modification.
        comment : str
            The comment of the modification.

        Returns:
        --------
        SheetModification
            The updated sheet modification.
        """
        with Session() as session:
            sheet_modification = (
                session.query(SheetModification)
                .filter(
                    SheetModification.user_id == user_id,
                    SheetModification.category_id == category_id,
                    SheetModification.name == name,
                )
                .first()
            )
            if value is not None:
                sheet_modification.value = value
            if attribute_type is not None:
                sheet_modification.attribute_type = attribute_type
            if status is not None:
                sheet_modification.status = status
            if comment is not None:
                sheet_modification.comment = comment
            sheet_modification.sheet_key = sheet_key
            session.commit()
            return sheet_modification


class RuleSystemRolls(Base):
    """
    A class representing a roll for a rule system.

    Attributes:
    -----------
    rule_system : str
        The rule system.
    name : str
        The name of the roll.
    roll : str
        The roll.
    """

    __tablename__ = "rule_system_rolls"
    rule_system: Mapped[str] = mapped_column(String, primary_key=True)
    name: Mapped[str] = mapped_column(String, primary_key=True)
    roll: Mapped[str] = mapped_column(String)

    @property
    def needed_sheet_values(self):
        """ Get the needed sheet values for the roll. """
        formula_blocks: list[str] = re.findall(r"\{([^\}]+)\}", self.roll)
        needed_sheet_values = set()
        for formula_block in formula_blocks:
            pruned_block = (
                formula_block.replace("+", " ")
                .replace("-", " ")
                .replace("*", " ")
                .replace("/", " ")
                .replace("(", " ")
                .replace(")", " ")
                .replace("  ", " ")
                .strip()
            )
            needed_sheet_values.update(pruned_block.split(" "))
        return needed_sheet_values

    def eval(self, sheet_values: dict[str, int]) -> int:
        """
        Evaluate the roll.

        Parameters:
        -----------
        sheet_values : dict[str,int]
            The values of the sheet.

        Returns:
        --------
        int
            The result of the roll.
        """
        formula_blocks: list[str] = re.findall(r"\{([^\}]+)\}", self.roll)
        eval_roll = self.roll
        for formula_block in formula_blocks:
            formula = formula_block
            for sheet_key, value in sheet_values.items():
                formula = formula.replace(sheet_key, value)
            eval_roll = eval_roll.replace(f"{{{formula_block}}}", eval(formula))
        return eval_roll

    @staticmethod
    def get(rule_system: str, name: str) -> "RuleSystemRolls":
        """
        Get a rule system roll.

        Parameters:
        -----------
        rule_system : str
            The rule system.
        name : str
            The name of the roll.

        Returns:
        --------
        RuleSystemRolls
            The rule system roll.
        """
        with Session() as session:
            return (
                session.query(RuleSystemRolls)
                .filter(RuleSystemRolls.rule_system == rule_system, RuleSystemRolls.name == name)
                .first()
            )

    @staticmethod
    def get_by_rule_system(rule_system: str) -> list["RuleSystemRolls"]:
        """
        Get all rule system rolls for a rule system.

        Parameters:
        -----------
        rule_system : str
            The rule system.

        Returns:
        --------
        list[RuleSystemRolls]
            A list of all rule system rolls for the rule system.
        """
        with Session() as session:
            return (
                session.query(RuleSystemRolls)
                .filter(RuleSystemRolls.rule_system == rule_system)
                .all()
            )

    @staticmethod
    def create(rule_system: str, name: str, roll: str) -> "RuleSystemRolls":
        """
        Create a new rule system roll.

        Parameters:
        -----------
        rule_system : str
            The rule system.
        name : str
            The name of the roll.
        roll : str
            The roll.

        Returns:
        --------
        RuleSystemRolls
            The created rule system roll.
        """
        with Session() as session:
            rule_system_roll = RuleSystemRolls(rule_system=rule_system, name=name, roll=roll)
            session.add(rule_system_roll)
            session.commit()
            return rule_system_roll

    @staticmethod
    def delete(rule_system: str, name: str) -> None:
        """
        Delete a rule system roll.

        Parameters:
        -----------
        rule_system : str
            The rule system.
        name : str
            The name of the roll.
        """
        with Session() as session:
            session.query(RuleSystemRolls).filter(
                RuleSystemRolls.rule_system == rule_system, RuleSystemRolls.name == name
            ).delete()
            session.commit()

    @staticmethod
    def update(rule_system: str, name: str, roll: str) -> "RuleSystemRolls":
        """
        Update a rule system roll.

        Parameters:
        -----------
        rule_system : str
            The rule system.
        name : str
            The name of the roll.
        roll : str
            The roll.
        """
        with Session() as session:
            rule_system_roll = (
                session.query(RuleSystemRolls)
                .filter(RuleSystemRolls.rule_system == rule_system, RuleSystemRolls.name == name)
                .first()
            )
            rule_system_roll.roll = roll
            session.commit()
            return rule_system_roll


class RuleSystemSuggestions(Base):
    """
    A class representing a suggestion for a rule system.

    Attributes:
    -----------
    id : int
        The unique identifier of the suggestion.
    rule_system : str
        The rule system the suggestion is for.
    suggested_key : str
        The suggested key.
    suggested_value : str
        The suggested value.
    """

    __tablename__ = "rule_system_suggestions"
    id: Mapped[str] = mapped_column(String, primary_key=True)
    rule_system: Mapped[str] = mapped_column(String)
    suggested_key: Mapped[str] = mapped_column(String)
    suggested_value: Mapped[str] = mapped_column(String)

    @staticmethod
    def get_by_rule_system(rule_system: str) -> list["RuleSystemSuggestions"]:
        """
        Get all rule system suggestions for a rule system.

        Parameters:
        -----------
        rule_system : str
            The rule system.

        Returns:
        --------
        list[RuleSystemSuggestions]
            A list of all rule system suggestions for the rule system.
        """
        with Session() as session:
            return (
                session.query(RuleSystemSuggestions)
                .filter(RuleSystemSuggestions.rule_system == rule_system)
                .all()
            )

    @staticmethod
    def create(
        rule_system: str, suggested_key: str, suggested_value: str
    ) -> "RuleSystemSuggestions":
        """
        Create a new rule system suggestion.

        Parameters:
        -----------
        rule_system : str
            The rule system.
        suggested_key : str
            The suggested key.
        suggested_value : str
            The suggested value.

        Returns:
        --------
        RuleSystemSuggestions
            The created rule system suggestion.
        """
        with Session() as session:
            rule_system_suggestion = RuleSystemSuggestions(
                rule_system=rule_system,
                suggested_key=suggested_key,
                suggested_value=suggested_value,
            )
            session.add(rule_system_suggestion)
            session.commit()
            return rule_system_suggestion

    @staticmethod
    def delete(rule_system_id: str) -> None:
        """
        Delete a rule system suggestion.

        Parameters:
        -----------
        id : int
            The unique identifier of the suggestion.
        """
        with Session() as session:
            session.query(RuleSystemSuggestions).filter(RuleSystemSuggestions.id == rule_system_id).delete()
            session.commit()

    @staticmethod
    def update(
        rule_system_id: str, suggested_key: str = None, suggested_value: str = None
    ) -> "RuleSystemSuggestions":
        """
        Update a rule system suggestion.

        Parameters:
        -----------
        id : int
            The unique identifier of the suggestion.
        suggested_key : str
            The suggested key.
        suggested_value : str
            The suggested value.

        Returns:
        --------
        RuleSystemSuggestions
            The updated rule system suggestion.
        """
        with Session() as session:
            rule_system_suggestion = (
                session.query(RuleSystemSuggestions).filter(RuleSystemSuggestions.id == rule_system_id).first()
            )
            if suggested_key is not None:
                rule_system_suggestion.suggested_key = suggested_key
            if suggested_value is not None:
                rule_system_suggestion.suggested_value = suggested_value
            session.commit()
            return rule_system_suggestion
