from pint import Quantity

from paebbl.telca.models.models.units import units

"""
================================================================================
 Model Class: FeedRatios
================================================================================

Purpose:
    To calculate the feed ratios of the additives in the slurry based on the feed rate and the ratios of rock to water.

Author:
    Veronica Bowman

Date:
    23/03/2025

Version:
    1.0

Verification Level:
    [2]
Validation Level:
    [B]

Assumptions:
    - Chemical Reactions proceed as defined in model documentation
    - No side reactions or losses
    - No additional additives outside of Acid / Alkali / Water / Rock
    - FeedRatios are only required for a fixed batch or addition and no recycling occurs
    - Percentages of Forsterite and Fayalite purity are known

Limitations:
    - [Known issues or constraints]
    - [External dependencies]

Inputs:
    - [percent_rock]: Decription: The percentage of rock required in the overall slurry mass
                    Units: percent
                    Valid Range: 0-100
                    Preferred Range: 5-40
    - [mols_NaHCO3]: Description: The number of moles of NaHCO3 required in the slurry
                    Units: mol/litre
                    Valid Range: 0-1
                    Preferred Range: 0.5-1
    - [mols_ascorbic_acid]: Description: The number of moles of ascorbic acid required in the slurry
                    Units: mol/litre
                    Valid Range: 0-1
                    Preferred Range: 0-0.1
    - [olivine_purity]: Description: The percentage of olivine in the rock
                    Units: percent
                    Valid Range: 0-100
                    Preferred Range: 90-100
    - [forsterite_purity]: Description: The percentage of forsterite in the olivine
                    Units: percent
                    Valid Range: 0-100
                    Preferred Range: 90-100
    - [old_volume]: Description: The original volume of slurry in the reactor
                    Units: litre
                    Valid Range: 0-10000
                    Preferred Range: 1000-5000
    - [remaining_volume]: Description: The volume of old slurry remaining in the reactor
                    Units: litre
                    Valid Range: 0-10000
                    Preferred Range: 1000-5000
    - [required_volume]: Description: The total volume of new slurry needed
                    Units: litre
                    Valid Range: 0-10000
                    Preferred Range: 1000-5000
    - [percent_rock_old]: Description: The percentage of rock in the old slurry
                    Units: percent
                    Valid Range: 0-100
                    Preferred Range: 5-40
    - [mols_NaHCO3_old]: Description: The number of moles of NaHCO3 in the old slurry
                    Units: mol/litre
                    Valid Range: 0-1
                    Preferred Range: 0.5-1
    - [mols_ascorbic_acid_old]: Description: The number of moles of ascorbic acid in the old slurry
                    Units: mol/litre
                    Valid Range: 0-1
                    Preferred Range: 0-0.1
    - [olivine_purity_old]: Description: The percentage of olivine in the old rock
                    Units: percent
                    Valid Range: 0-100
                    Preferred Range: 90-100
    - [forsterite_purity_old]: Description: The percentage of forsterite in the old olivine
                    Units: percent
                    Valid Range: 0-100
                    Preferred Range: 90-100
    - [percent_rock_new]: Description: The percentage of rock required in the new slurry
                    Units: percent
                    Valid Range: 0-100
                    Preferred Range: 5-40
    - [mols_NaHCO3_new]: Description: The number of moles of NaHCO3 in the new slurry
                    Units: mol/litre
                    Valid Range: 0-1
                    Preferred Range: 0.5-1
    - [mols_ascorbic_acid_new]: Description: The number of moles of ascorbic acid in the new slurry
                    Units: mol/litre
                    Valid Range: 0-1
                    Preferred Range: 0-0.1
    - [olivine_purity_new]: Description: The percentage of olivine in the new rock
                    Units: percent
                    Valid Range: 0-100
                    Preferred Range: 90-100
    - [forsterite_purity_new]: Description: The percentage of forsterite in the new olivine
                    Units: percent
                    Valid Range: 0-100
                    Preferred Range: 90-100

Outputs:
"percent_NaHCO3": percent_NaHCO3,
            "percent_ascorbic_acid": percent_ascorbic_acid,
            "percent_water": percent_water,
            "percent_crap": percent_crap,
            "percent_fayalite": percent_fayalite,
            "percent_forsterite": percent_forsterite,
             output_quantities["NaHCO3"] = output_quantities_full["NaHCO3"]
        output_quantities["ascorbic_acid"] = output_quantities_full["ascorbic_acid"]
        output_quantities["water"] = output_quantities_full["water"]

        # Sum the last three elements (rock components)
        rock_total = (
        slurry_density = slurry_density
    - [percent_NaHCO3]: Description:  The precentage mass of soda in the output slurry
                        Units: percent
                        Valid Range: 0-100
    - [percent_ascorbic_acid]: Description: The precentage mass of ascorbic acid in the output slurry
                        Units: percent
                        Valid Range: 0-100
    - [percent_water]: Description: The precentage mass of water in the output slurry
                        Units: percent
                        Valid Range: 0-100
    - [percent_crap]: Description: The precentage mass of crap in the output slurry
                        Units: percent
                        Valid Range: 0-100
    - [percent_fayalite]: Description: The precentage mass of fayalite in the output slurry
                        Units: percent
                        Valid Range: 0-100
    - [percent_forsterite]: Description: The precentage mass of forsterite in the output slurry
                        Units: percent
                        Valid Range: 0-100
    - [output_quantities]: Description: The mass of each component that needs to be added to a new mix
                        Units: kg
    - [rock_total]: Description: The total mass of rock in the output slurry
                        Units: kg

References:
    - [Link or citation to underpinning theory or data]
    - [Associated literature or validation report]

Test Coverage:
    - Unit Tests: [Yes/No/Partial]
    - Scenario Tests: [No]
    - Verified Envelope: [Link to documentation or description]

Usage Notes:
    - [Optional tips, warnings, or best practices for use]

Maintenance:
    - [Veronica Bowman]
    - [Yearly review required: Yes]
    - [Yearly review date: 23/03/2026]

Review Technical:
    - [Walter Devries]
    - [Comments: ]
    - [Approval: Yes/No]
    - [Approval Date: ]
Review Code:
    - [David Pugh]
    - [Comments: ]
    - [Approval: Yes/No]
    - [Approval Date: ]
================================================================================
"""
# these should be read from file
NaHCO3_mol_weight = 84.0 * units.gram / units.mol # i haven't checked the numbers to the decimals, we can fix this in the read file and add significance
ascorbic_acid_mol_weight = 176.0 * units.gram / units.mol
water_mol_weight = 18.0 * units.gram / units.mol
fayalite_mol_weight = 204.0 * units.gram / units.mol
SiO2_Fa_mol_weight = 60.0 * units.gram / units.mol
FeCO3_mol_weight = 116.0 * units.gram / units.mol
Forsterite_mol_weight = 141.0 * units.gram / units.mol
MgCO3_mol_weight = 84.0 * units.gram / units.mol
CO2_Fa_mol_weight = 44.0 * units.gram / units.mol

NaHCO3_density = 2.2 * units.kilogram / units.litre#wiki
ascorbic_acid_density = 1.65 * units.kilogram / units.litre#wiki
water_density = 1.0 * units.kilogram / units.litre#wiki
crap_density = 4.61 * units.kilogram / units.litre # this number was derived from the density of OMS2 which is 3.74kg/l as given by Recipe calculator of Louk. I havent verified this number
fayalite_density = 4.3 * units.kilogram / units.litre #wiki
SiO2_Fa_density = 2.65 * units.kilogram / units.litre #wiki
FeCO3_density = 3.9 * units.kilogram / units.litre #wiki
forsterite_density = 3.2 * units.kilogram / units.litre     #wiki 
MgCO3_density = 2.95 * units.kilogram / units.litre    #wiki
CO2_Fa_density = 0.65 * units.kilogram / units.litre # you shouldn't need this number in the current calculation. It is dependent on pressure and temperature, so it is not a constant. 
class FeedRatios:
    def __init__(self, feed_ratios: dict[str, Quantity]):
        """
        Initializes the Ratios class without predefined values.
        """
        self.feed_ratios = feed_ratios

    def validate_percentage_values(self):
        """
        Validate the percentages.
        """
        total = sum(self.feed_ratios.values())
        if total.magnitude != 100:
            raise ValueError("Feed ratios must sum to 100%.")

    def __repr__(self):
        """
        String representation of the class showing values and their percentages.
        """
        return str(self.feed_ratios)

    def set_values(self, *values):
        """
        Set values for each additive in the dictionary.

        Parameters:
        -----------
        *values : float or Quantity
            Values for each additive in the order they were provided in the constructor.

        Raises:
        -------
        ValueError
            If the number of values doesn't match the number of additives.
        """
        additives = list(self.feed_ratios.keys())

        if len(values) != len(additives):
            raise ValueError(f"Expected {len(additives)} values, got {len(values)}")

        for i, additive in enumerate(additives):
            value = values[i]
            # Convert to Quantity if it's not already
            if not isinstance(value, Quantity):
                value = value * units.percent
            self.feed_ratios[additive] = value

        # Optionally validate the percentages sum to 100%
        try:
            self.validate_percentage_values()
        except ValueError as e:
            print(f"Warning: {e}")

    def calculate_mass_percentages_from_mols_feedrate(
        self,
        percent_rock: Quantity,
        mols_NaHCO3: Quantity, #Technially this is a Molar, not mols. It is the molar concentration in Mol/litre of water (i check with Fay that it is NOT per liter of solution)
        mols_ascorbic_acid: Quantity, #idem
        olivine_purity: Quantity, #defined as olivine/rock
        forsterite_purity: Quantity, #defined as forsterite/olivine
    ):
        """
        Calculate the ratios of the feed using mass balance, the feed rate and the ratios of rock to water.
        """
        percent_fluid = 100 * units.percent - percent_rock #this is fluid including additives, so fluid - additives = water
        # kg mass of the additives
        # Calculate ascorbic_acid
        mass_ascorbic_acid = (
            (mols_ascorbic_acid * ascorbic_acid_mol_weight) / water_density #mol acid/liter water x gram acid/mol acid / kg water/liter water = kg acid/liter water   
        ).to_reduced_units() # so this is not mass, it is the kg of acid in a liter of water
        mass_NaHCO3 = (
            (mols_NaHCO3 * NaHCO3_mol_weight) / water_density
        ).to_reduced_units()

        # Percent of Water
        percent_water = percent_fluid / (mass_ascorbic_acid + mass_NaHCO3 + 1) #check -> correct but it is not the mass of acid, it is the mass of acid in a liter of water

        # Percent additives
        percent_NaHCO3 = mass_NaHCO3 * percent_water #in excel I also had 1000, but I assume your units function takes care of that. Please validate this assumption.
        percent_ascorbic_acid = mass_ascorbic_acid * percent_water

        # Calculate the mass of the crap
        percent_crap = (percent_rock) * (
            1 - (olivine_purity.magnitude / 100)
        )  # * units.percent # convert to a ratio and the crap is what is not olivine
        percent_forsterite = (
            percent_rock
            * olivine_purity.magnitude
            / 100 #personally I just hate the devision by 100, but I assume it is needed to convert the percent to a ratio
            * forsterite_purity.magnitude
            / 100
        )  # (((percent_rock / 100) * olivine_purity) / 100) * forsterite_purity #* units.percent
        percent_fayalite = percent_rock - percent_crap - percent_forsterite #yes this can also work. I did it as percent_rock * olivine_purity * (1 - forsterite_purity) / 100, but this is also correct. I think it is a bit more readable like this, but it is up to you.

        outputs = {
            "percent_NaHCO3": percent_NaHCO3,
            "percent_ascorbic_acid": percent_ascorbic_acid,
            "percent_water": percent_water,
            "percent_crap": percent_crap,
            "percent_fayalite": percent_fayalite,
            "percent_forsterite": percent_forsterite,
        }

        return outputs

    def calculate_recipe_addition(
        self,
        old_volume: Quantity, #I assume this is the volume left in the feedvessel
        remaining_volume: Quantity, # this is total volume minus old_volume
        required_volume: Quantity, # this is the volume of the new slurry needed?
        percent_rock_old: Quantity,
        mols_NaHCO3_old: Quantity,
        mols_ascorbic_acid_old: Quantity,
        olivine_purity_old: Quantity,
        forsterite_purity_old: Quantity,
        percent_rock_new: Quantity,
        mols_NaHCO3_new: Quantity,
        mols_ascorbic_acid_new: Quantity,
        olivine_purity_new: Quantity,
        forsterite_purity_new: Quantity,
    ):
        """
        Calculate the recipe addition based on the volume of the reactor and the volume of the slurry. 
        Parameters:
        -----------
        old_volume: Quantity
            The original volume of slurry in the reactor
        remaining_volume: Quantity
            The volume of old slurry remaining in the reactor
        required_volume: Quantity
            The total volume of new slurry needed
        percent_rock_old, mols_NaHCO3_old, etc.: Quantity
            Parameters describing the old slurry composition
        percent_rock_new, mols_NaHCO3_new, etc.: Quantity
            Parameters describing the desired new slurry composition

        Returns:
        --------
        dict[str, Quantity]
        Dictionary containing the amounts of each component that need to be added

        """
        old_ratios = self.calculate_mass_percentages_from_mols_feedrate(
            percent_rock_old,
            mols_NaHCO3_old,
            mols_ascorbic_acid_old,
            olivine_purity_old,
            forsterite_purity_old,
        )
        new_ratios = self.calculate_mass_percentages_from_mols_feedrate(
            percent_rock_new,
            mols_NaHCO3_new,
            mols_ascorbic_acid_new,
            olivine_purity_new,
            forsterite_purity_new,
        )

        slurry_density_old = self.calculate_slurry_density_per_litre(old_ratios)
        slurry_density_new = self.calculate_slurry_density_per_litre(new_ratios)
        feed_rate_old = old_volume * slurry_density_old  # so here we go from volume to mass, but you declare it as a rate. Im not (yet) following what you are doing here.
        feed_rate_new = required_volume * slurry_density_new

        new_masses = {}
        for component in new_ratios.keys():
            new_masses[component] = (
                new_ratios[component].magnitude / 100
            ) * feed_rate_new # so here we calculate the mass needed for each constituent

        old_masses = {}
        for component in old_ratios.keys():
            old_masses[component] = (
                old_ratios[component].magnitude / 100
            ) * feed_rate_old

        # proportion needed
        prop_left = remaining_volume / old_volume # I need to understand your definitions here. Not sure where this is going.

        # Initialize the output dictionary
        output_quantities_full = {}

# i think you are calculating what we need to add to the vessel to obtain the new recipe, but I'm not sure. Lets discuss first.
        for component in old_ratios.keys():
            # Calculate total amount needed in the new mixture
            new_amount_total = new_masses[component] - prop_left * old_masses[component]

            # Store in output dictionary
            output_quantities_full[component.replace("percent_", "")] = new_amount_total

        # Create a new dictionary with the first three elements unchanged
        # and a final entry that is the sum of the last three entries
        output_quantities = {}

        # Copy the first three elements (additives)
        output_quantities["NaHCO3"] = output_quantities_full["NaHCO3"]
        output_quantities["ascorbic_acid"] = output_quantities_full["ascorbic_acid"]
        output_quantities["water"] = output_quantities_full["water"]

        # Sum the last three elements (rock components)
        rock_total = (
            output_quantities_full["crap"]
            + output_quantities_full["fayalite"]
            + output_quantities_full["forsterite"]
        )
        output_quantities["rock"] = rock_total

        return output_quantities

    def calculate_slurry_density_per_litre(self, feed_ratios: dict[str, Quantity]):
        """
        Calculate the total slurry density per litre based on the percentages.
        """
        # Create a density mapping to look up the actual density values
        density_mapping = {
            "percent_NaHCO3": NaHCO3_density,
            "percent_ascorbic_acid": ascorbic_acid_density,
            "percent_water": water_density,
            "percent_crap": crap_density,
            "percent_fayalite": fayalite_density,
            "percent_forsterite": forsterite_density,
        }

        # Initialize with appropriate units
        initial_sum = 0.0
        for key, value in feed_ratios.items():
            if key in density_mapping:
                # Calculate volume fraction (percentage / density)
                initial_sum += value / density_mapping[key] # so this takes the mass-percentage of each constituent and divides by density of the same constituent -> correct.
            else:
                raise ValueError(f"No density mapping for component: {key}")

        # Calculate slurry density
        slurry_density = sum(feed_ratios.values()) / initial_sum
        return slurry_density #checked. Ok.


# Example Usage
# I assume this is just to check with 'my excel' and 'Louks excel' Be aware that 'Louks excel has a slight error in calculating the total volume not including addtives.
# at the moment I cannot run the code, so I cannot check this, But I want to do this later.
if __name__ == "__main__":
    list_of_inputs = [
        "NaHCO3",
        "ascorbic_acid",
        "water",
        "crap",
        "fayalite",
        "forsterite",
    ]

    # Create dictionary with default values (zero percentages)
    feed_dict = {additive: 0.0 * units.percent for additive in list_of_inputs}

    # Now create the FeedRatios instance with the dictionary
    r = FeedRatios(feed_dict)
    # r.set_values(3.17 * units.percent, 0.1 * units.percent, 58 * units.percent, 1.9 * units.percent, 0.1 * units.percent, 34.9 * units.percent)
    out = r.calculate_mass_percentages_from_mols_feedrate(
        5 * units.percent,
        0.65 * units.mol / units.litre,
        0.01 * units.mol / units.litre,
        55 * units.percent,
        95 * units.percent,
    )
    # print(r)
    print(f"mass percentages: {out}")

    slurry_density = r.calculate_slurry_density_per_litre(out)

    recipe_addition = r.calculate_recipe_addition(
        6000 * units.litre / units.hour,
        3000 * units.litre / units.hour,
        5000 * units.litre / units.hour,
        5 * units.percent,
        0.65 * units.mol / units.litre,
        0.01 * units.mol / units.litre,
        55 * units.percent,
        95 * units.percent,
        35 * units.percent,
        0.65 * units.mol / units.litre,
        0.01 * units.mol / units.litre,
        55 * units.percent,
        95 * units.percent,
    )
    print(f"\nslurry density {slurry_density}")
    print(f"\nrecipe addition {recipe_addition}")
# Add these imports at the top of the file (after your existing imports)


# # # Add this test class at the end of the file (after the if __name__ == "__main__" block)
#     class TestFeedRatios(unittest.TestCase):
#      """Unit tests for the FeedRatios class."""

#     def setUp(self):
#         """Set up test fixtures."""
#         self.additives = ["NaHCO3", "ascorbic_acid", "water", "crap", "fayalite", "forsterite"]
#         self.feed_dict = {additive: 0.0 * units.percent for additive in self.additives}
#         self.ratios = FeedRatios(self.feed_dict)

#     def test_init(self):
#         """Test initializing the FeedRatios class."""
#         self.assertIsInstance(self.ratios, FeedRatios)
#         self.assertEqual(len(self.ratios.feed_ratios), 6)

#     def test_set_values(self):
#         """Test setting values for additives."""
#         # Test setting values as numbers (should be converted to percent)
#         self.ratios.set_values(10, 5, 60, 5, 10, 10)
#         self.assertEqual(self.ratios.feed_ratios["NaHCO3"], 10 * units.percent)
#         self.assertEqual(self.ratios.feed_ratios["ascorbic_acid"], 5 * units.percent)

#         # Test setting values as quantities
#         test_values = [
#             15 * units.percent,
#             5 * units.percent,
#             50 * units.percent,
#             10 * units.percent,
#             10 * units.percent,
#             10 * units.percent
#         ]
#         self.ratios.set_values(*test_values)
#         self.assertEqual(self.ratios.feed_ratios["NaHCO3"], 15 * units.percent)

#         # Test ValueError when wrong number of values
#         with self.assertRaises(ValueError):
#             self.ratios.set_values(10, 20, 30)

#     def test_validate_percentage_values(self):
#         """Test validating that percentages sum to 100%."""
#         # Test valid total (100%)
#         self.ratios.set_values(10, 15, 25, 20, 15, 15)
#         try:
#             self.ratios.validate_percentage_values()
#         except ValueError:
#             self.fail("validate_percentage_values() raised ValueError unexpectedly!")

#         # Test invalid total (not 100%)
#         self.ratios.set_values(10, 10, 10, 10, 10, 10)  # Total 60%
#         with self.assertRaises(ValueError):
#             self.ratios.validate_percentage_values()

#     def test_calculate_mass_percentages_from_mols_feedrate(self):
#         """Test calculating mass percentages from molar feedrates."""
#         # Test with typical values
#         result = self.ratios.calculate_mass_percentages_from_mols_feedrate(
#             30 * units.percent,
#             0.65 * units.mol / units.litre,
#             0.01 * units.mol / units.litre,
#             55 * units.percent,
#             95 * units.percent
#         )

#         # Check all expected keys are present
#         expected_keys = [
#             "percent_NaHCO3", "percent_ascorbic_acid", "percent_water",
#             "percent_crap", "percent_fayalite", "percent_forsterite"
#         ]
#         for key in expected_keys:
#             self.assertIn(key, result)

#         # Check result values are reasonable
#         self.assertGreater(result["percent_water"], 50 * units.percent)  # Water should be majority
#         self.assertLess(result["percent_ascorbic_acid"], 5 * units.percent)  # Small amount of acid

#         # Check total percentages add up to 100% (allowing for float precision)
#         total = sum(result.values())
#         self.assertAlmostEqual(total.magnitude, 100, places=5)

#         # Test with different rock percentages
#         high_rock = self.ratios.calculate_mass_percentages_from_mols_feedrate(
#             70 * units.percent,
#             0.65 * units.mol / units.litre,
#             0.01 * units.mol / units.litre,
#             55 * units.percent,
#             95 * units.percent
#         )
#         low_rock = self.ratios.calculate_mass_percentages_from_mols_feedrate(
#             10 * units.percent,
#             0.65 * units.mol / units.litre,
#             0.01 * units.mol / units.litre,
#             55 * units.percent,
#             95 * units.percent
#         )

#         # Higher rock percentage should result in more rock components
#         self.assertGreater(
#             high_rock["percent_forsterite"] + high_rock["percent_fayalite"] + high_rock["percent_crap"],
#             low_rock["percent_forsterite"] + low_rock["percent_fayalite"] + low_rock["percent_crap"]
#         )

#     def test_calculate_slurry_density_per_litre(self):
#         """Test calculating slurry density from component percentages."""
#         # Calculate feed ratios first
#         feed_ratios = self.ratios.calculate_mass_percentages_from_mols_feedrate(
#             30 * units.percent,
#             0.65 * units.mol / units.litre,
#             0.01 * units.mol / units.litre,
#             55 * units.percent,
#             95 * units.percent
#         )

#         # Calculate density
#         density = self.ratios.calculate_slurry_density_per_litre(feed_ratios)

#         # Basic sanity checks on the density value
#         self.assertGreater(density, 1.0 * units.kilogram / units.litre)  # Should be greater than water
#         self.assertLess(density, 5.0 * units.kilogram / units.litre)  # Should be less than solid rock

#         # Test with invalid component (missing density mapping)
#         invalid_feed_ratios = {"invalid_component": 100 * units.percent}
#         with self.assertRaises(ValueError):
#             self.ratios.calculate_slurry_density_per_litre(invalid_feed_ratios)

#     def test_calculate_recipe_addition(self):
#         """Test calculating recipe addition for changing volumes."""
#         # Test with typical values
#         recipe = self.ratios.calculate_recipe_addition(
#             6000 * units.litre,
#             3000 * units.litre,
#             5000 * units.litre,
#             5 * units.percent,
#             0.65 * units.mol / units.litre,
#             0.01 * units.mol / units.litre,
#             55 * units.percent,
#             95 * units.percent,
#             35 * units.percent,
#             0.65 * units.mol / units.litre,
#             0.01 * units.mol / units.litre,
#             55 * units.percent,
#             95 * units.percent
#         )

#         # Check expected keys in output
#         expected_keys = ["NaHCO3", "ascorbic_acid", "water", "rock"]
#         for key in expected_keys:
#             self.assertIn(key, recipe)

#         # Since we're going from 5% rock to 35% rock, the rock component should be positive
#         self.assertGreater(recipe["rock"].magnitude, 0)

#         # Test reducing rock content (should result in negative or zero rock addition)
#         recipe_reduce_rock = self.ratios.calculate_recipe_addition(
#             6000 * units.litre,
#             3000 * units.litre,
#             5000 * units.litre,
#             35 * units.percent,  # High initial rock content
#             0.65 * units.mol / units.litre,
#             0.01 * units.mol / units.litre,
#             55 * units.percent,
#             95 * units.percent,
#             5 * units.percent,   # Low target rock content
#             0.65 * units.mol / units.litre,
#             0.01 * units.mol / units.litre,
#             55 * units.percent,
#             95 * units.percent
#         )

#         # Since we're going from 35% rock to 5% rock, more water should be added
#         self.assertGreater(recipe_reduce_rock["water"].magnitude, recipe["water"].magnitude)

#     def test_corner_cases(self):
#         """Test corner cases and edge conditions."""
#         # Test with zero rock
#         zero_rock = self.ratios.calculate_mass_percentages_from_mols_feedrate(
#             0 * units.percent,
#             0.65 * units.mol / units.litre,
#             0.01 * units.mol / units.litre,
#             55 * units.percent,
#             95 * units.percent
#         )
#         self.assertEqual(zero_rock["percent_crap"].magnitude, 0)
#         self.assertEqual(zero_rock["percent_fayalite"].magnitude, 0)
#         self.assertEqual(zero_rock["percent_forsterite"].magnitude, 0)

#         # Test with 100% rock (edge case)
#         all_rock = self.ratios.calculate_mass_percentages_from_mols_feedrate(
#             100 * units.percent,
#             0.65 * units.mol / units.litre,
#             0.01 * units.mol / units.litre,
#             55 * units.percent,
#             95 * units.percent
#         )
#         self.assertEqual(all_rock["percent_water"].magnitude, 0)

#         # Test with no remaining volume (complete replacement)
#         full_replacement = self.ratios.calculate_recipe_addition(
#             5000 * units.litre,
#             0 * units.litre,  # No remaining volume
#             5000 * units.litre,
#             30 * units.percent,
#             0.65 * units.mol / units.litre,
#             0.01 * units.mol / units.litre,
#             55 * units.percent,
#             95 * units.percent,
#             30 * units.percent,
#             0.65 * units.mol / units.litre,
#             0.01 * units.mol / units.litre,
#             55 * units.percent,
#             95 * units.percent
#         )
#         # For full replacement, output should match expected component quantities

# # Add this to the end of your file to run the tests when executing this module directly
# if __name__ == "__main__":
#     # Comment out the example code to avoid it running during tests
#     # list_of_inputs = [...]
#     # ... rest of your example code ...

#     # Run the tests
#     unittest.main()
