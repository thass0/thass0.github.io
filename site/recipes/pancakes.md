---
layout: recipe
---

# Banana Pancakes

<div class="recipe-controls">
    <label for="banana-scale">Scale: </label>
    <input type="range" id="banana-scale" min="0.5" max="4" step="0.1" value="1">
    <span id="banana-scale-value">1.0x</span>
</div>
<div id="banana-ingredients">
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

<script>
document.addEventListener('DOMContentLoaded', function() {
    setupRecipeScaling('banana-scale', 'banana-scale-value', 'banana-ingredients');
});
</script>
