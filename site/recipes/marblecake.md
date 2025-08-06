---
layout: recipe
---

## Marble Cake

<div class="recipe-controls">
    <label for="marble-scale">Scale: </label>
    <input type="range" id="marble-scale" min="0.5" max="4" step="0.1" value="1">
    <span id="marble-scale-value">1.0x</span>
</div>
<div id="marble-ingredients">
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

<script>
document.addEventListener('DOMContentLoaded', function() {
    setupRecipeScaling('marble-scale', 'marble-scale-value', 'marble-ingredients');
});
</script>
