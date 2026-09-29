import pint

# Create the unit registry
unit_registry = pint.UnitRegistry()
unit_registry.default_system = "SI"  # Set the default system to SI units
unit_registry.formatter.default_format = "~"  # Use abbreviated unit names
pint.set_application_registry(unit_registry)  # type: ignore


def convert_to_base_units(value: float, unit: pint.Unit) -> float:
    """
    Converts a value with a given unit to its base unit representation.

    Args:
        value: The value to convert.
        unit: The unit of the value.

    Returns:
        The value converted to its base unit representation.
    """

    return (value * unit_registry.Unit(unit)).to_base_units().magnitude  # type: ignore


def convert_from_base_units(value: float, unit: pint.Unit) -> float:
    """
    Converts a value in base units to a specified unit.

    Args:
        value: The value in base units.
        unit: The unit to which the value will be converted.

    Returns:
        The value converted to the specified unit.
    """

    base_units: pint.Unit = unit_registry.Unit((1 * unit).to_base_units().units)  # type: ignore

    return (value * base_units).to(unit).magnitude  # type: ignore
