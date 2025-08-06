---
layout: default
---

# Recipes

## Marble Cake

<div class="recipe-ingredients">
    <div class="recipe-controls">
        <label for="marble-scale">Scale: </label>
        <input type="range" id="marble-scale" min="0.5" max="4" step="0.1" value="1">
        <span id="marble-scale-value">1.0x</span>
    </div>

    <p><strong>Ingredients:</strong></p>
    <ul>
    <li><span data-base="200" data-unit="g" data-roundto="25">200g</span> butter</li>
    <li><span data-base="250" data-unit="g" data-roundto="25">250g</span> sugar</li>
    <li><span data-base="125" data-unit="g" data-roundto="25">125g</span> flour</li>
    <li><span data-base="125" data-unit="g" data-roundto="25">125g</span> cornstarch</li>
    <li><span data-base="0.5" data-unit="tsp" data-unit-plural="tsp" data-roundto="0.25">½ tsp</span> baking powder</li>
    <li><span data-base="1" data-unit="packet" data-unit-plural="packets" data-roundto="0.5">1 packet</span> vanilla sugar</li>
    <li><span data-base="4" data-unit="egg" data-unit-plural="eggs" data-roundto="1">4 eggs</span></li>
    <li><span data-base="2" data-unit="tbsp" data-unit-plural="tbsp" data-roundto="0.5">2 tbsp</span> cocoa</li>
    <li><span data-base="2" data-unit="tbsp" data-unit-plural="tbsp" data-roundto="0.5">2 tbsp</span> sugar (for cocoa)</li>
    </ul>
</div>

**Instructions:**
1. Put butter in mixing bowl and cream with sugar, flour/cornstarch, eggs, vanilla sugar and baking powder.
2. Put half of the batter into the greased cake pan, add cocoa and sugar to the other half and mix.
3. Preheat oven for 15 minutes at 175°C with bottom heat.
4. Bake on the lower rack with for 60 minutes.
5. Leave the cake in the oven for another 10 minutes after turning off the oven.

## Banana Pancakes

<div class="recipe-ingredients">
    <div class="recipe-controls">
        <label for="banana-scale">Scale: </label>
        <input type="range" id="banana-scale" min="0.5" max="4" step="0.1" value="1">
        <span id="banana-scale-value">1.0x</span>
    </div>

    <p><strong>Ingredients:</strong> (makes 6 thick to 10 thin pancakes)</p>
    <ul>
    <li><span data-base="5" data-unit="banana" data-unit-plural="bananas" data-roundto="1">5 ripe bananas</span></li>
    <li><span data-base="4" data-unit="egg" data-unit-plural="eggs" data-roundto="1">4 eggs</span></li>
    <li><span data-base="300" data-unit="ml" data-roundto="25">300ml</span> (plant-based) milk</li>
    <li><span data-base="300" data-unit="g" data-roundto="25">300g</span> wheat or spelt flour</li>
    <li><span data-base="1" data-unit="pinch" data-unit-plural="pinches" data-roundto="1">1 pinch</span> salt</li>
    <li>Butter for frying</li>
    </ul>
</div>

**Instructions:**
1. Mash bananas in a bowl with a fork to puree
2. Add eggs and milk and stir
3. Stir in flour and salt
4. Heat pan to medium heat
5. Fry each pancake on both sides with some butter

<style>
.recipe-controls {
    margin: 1em 0;
    padding: 0.5em;
    background: #f5f5f5;
    border-radius: 4px;
}

.recipe-controls label {
    font-weight: bold;
    margin-right: 0.5em;
}

.recipe-controls input[type="range"] {
    margin: 0 0.5em;
    width: 200px;
}
</style>

<script>
function roundToNearest25(value) {
    return Math.round(value / 25) * 25;
}

function roundToInteger(value) {
    return Math.round(value);
}

function roundToHalf(value) {
    return Math.round(value * 2) / 2;
}

function updateIngredient(element, scale) {
    const base = parseFloat(element.dataset.base);
    const unit = element.dataset.unit;
    const unitPlural = element.dataset.unitPlural;
    const roundTo = parseFloat(element.dataset.roundto);

    let scaledValue = base * scale;
    let displayValue = Math.round(scaledValue / roundTo) * roundTo;

    let displayText;
    const fractionalPart = displayValue % 1;
    const wholePart = Math.floor(displayValue);

    if (Math.abs(fractionalPart - 0.25) < 0.001) {
        displayText = wholePart === 0 ? "¼" : wholePart + "¼";
    } else if (Math.abs(fractionalPart - 0.5) < 0.001) {
        displayText = wholePart === 0 ? "½" : wholePart + "½";
    } else if (Math.abs(fractionalPart - 0.75) < 0.001) {
        displayText = wholePart === 0 ? "¾" : wholePart + "¾";
    } else {
        displayText = displayValue.toString();
    }

    let finalUnit = unit;
    if (unitPlural && displayValue !== 1) {
        finalUnit = unitPlural;
    }

    if (unit === 'g' || unit === 'ml') {
        element.textContent = displayText + finalUnit;
    } else {
        element.textContent = displayText + ' ' + finalUnit;
    }
}

function setupRecipeScaling(scaleId, valueId) {
    const slider = document.getElementById(scaleId);
    const valueDisplay = document.getElementById(valueId);
    const container = slider.closest('.recipe-ingredients');

    // Reset slider position on page load
    slider.value = '1';
    valueDisplay.textContent = '1.0x';

    slider.addEventListener('input', function() {
        const scale = parseFloat(this.value);
        valueDisplay.textContent = scale.toFixed(1) + 'x';

        const ingredients = container.querySelectorAll('[data-base]');
        ingredients.forEach(ingredient => {
            updateIngredient(ingredient, scale);
        });
    });
}

document.addEventListener('DOMContentLoaded', function() {
    setupRecipeScaling('marble-scale', 'marble-scale-value');
    setupRecipeScaling('banana-scale', 'banana-scale-value');
});
</script>
