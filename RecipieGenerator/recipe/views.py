import re
from django.http import JsonResponse
from django.shortcuts import render
from transformers import pipeline, GPT2Tokenizer, GPT2LMHeadModel
from diffusers import StableDiffusionPipeline
import torch
import base64
from io import BytesIO
from PIL import Image

# Lazy loading of models to avoid startup delays
generator = None
image_generator = None
recipe_tokenizer = None
recipe_model = None

def load_generator():
    global generator
    if generator is None:
        generator = pipeline("text-generation", model="gpt2-medium", device=-1)
        generator.tokenizer.pad_token = generator.tokenizer.eos_token
    return generator

def load_image_generator():
    global image_generator
    if image_generator is None:
        image_generator = StableDiffusionPipeline.from_pretrained(
            "stabilityai/stable-diffusion-2-1", 
            torch_dtype=torch.float32,
            use_safetensors=True
        ).to("cpu")
    return image_generator

def load_recipe_models():
    global recipe_tokenizer, recipe_model
    if recipe_tokenizer is None:
        recipe_model_name = "mbien/recipenlg"
        recipe_tokenizer = GPT2Tokenizer.from_pretrained(recipe_model_name)
        recipe_tokenizer.pad_token = recipe_tokenizer.eos_token
        recipe_model = GPT2LMHeadModel.from_pretrained(recipe_model_name)
    return recipe_tokenizer, recipe_model

def Home(request):
    return render(request, "Home.html")

def GenerateRecipe(dish_name):
    try:
        print(f"🔄 Generating recipe for: {dish_name}")
        
        # Simple recipe generator with basic templates
        recipes_db = {
            "pizza": {
                "ingredients": "2 cups flour, 1 cup water, 2 tbsp olive oil, 1 cup tomato sauce, 2 cups mozzarella cheese, salt and pepper to taste, fresh basil",
                "instructions": "1. Mix flour and water. 2. Add olive oil and knead dough. 3. Let it rest for 30 minutes. 4. Spread tomato sauce on dough. 5. Add cheese and toppings. 6. Bake at 400°F for 12-15 minutes."
            },
            "tacos": {
                "ingredients": "8 taco shells, 1 lb ground beef, 1 onion, 2 cloves garlic, 1 cup lettuce, 1 cup tomatoes, 1 cup cheese, sour cream, taco seasoning",
                "instructions": "1. Brown ground beef with onion and garlic. 2. Add taco seasoning and water. 3. Simmer for 5 minutes. 4. Warm taco shells. 5. Fill with meat mixture. 6. Add lettuce, tomatoes, and cheese. 7. Top with sour cream."
            },
            "burger": {
                "ingredients": "1 lb ground beef, 4 burger buns, 1 onion, 4 lettuce leaves, 4 tomato slices, 1 cup cheese, salt and pepper, optional toppings",
                "instructions": "1. Form ground beef into 4 patties. 2. Season with salt and pepper. 3. Cook on grill or pan for 3-4 minutes per side. 4. Toast buns. 5. Assemble burger with cheese, lettuce, tomato, and onion."
            },
            "biryani": {
                "ingredients": "2 cups basmati rice, 1 kg chicken, 2 onions, 4 cloves garlic, 2 tbsp ginger-garlic paste, 1 cup yogurt, saffron, ghee, spices (cumin, cinnamon, bay leaves)",
                "instructions": "1. Soak rice for 30 minutes. 2. Marinate chicken in yogurt and spices for 2 hours. 3. Caramelize onions. 4. Layer rice and chicken in pot. 5. Add saffron and ghee. 6. Cook on high heat for 2 minutes, then low heat for 45 minutes."
            },
            "pasta": {
                "ingredients": "1 lb pasta, 2 cups tomato sauce, 3 cloves garlic, 1/4 cup olive oil, 1 cup parmesan cheese, fresh basil, salt and pepper",
                "instructions": "1. Boil water and add pasta. 2. Cook until al dente, about 8-10 minutes. 3. Heat olive oil and sauté garlic. 4. Add tomato sauce and simmer for 10 minutes. 5. Drain pasta and mix with sauce. 6. Top with parmesan and basil."
            },
            "samosa": {
                "ingredients": "2 cups flour, 1 cup potatoes (boiled), 1/2 cup peas, 1 onion, 2 cloves garlic, spices (cumin, coriander), oil for frying, water",
                "instructions": "1. Make dough with flour and water. 2. Roll thin and cut triangles. 3. Cook potatoes, peas, and spices for filling. 4. Fill samosa and fold. 5. Deep fry at 350°F until golden. 6. Serve with chutney."
            },
            "chicken": {
                "ingredients": "2 lbs chicken breast, 3 cloves garlic, 2 tbsp soy sauce, 2 tbsp olive oil, 1 lemon, fresh herbs, salt and pepper",
                "instructions": "1. Marinate chicken in garlic, soy sauce, olive oil, and lemon juice for 30 minutes. 2. Heat grill or pan to high heat. 3. Cook chicken for 6-7 minutes per side. 4. Let rest for 5 minutes. 5. Serve with fresh herbs."
            }
        }
        
        # Get recipe for the dish or generate a generic one
        if dish_name.lower() in recipes_db:
            recipe_data = recipes_db[dish_name.lower()]
            ingredients = recipe_data["ingredients"]
            instructions = recipe_data["instructions"]
        else:
            # Generic fallback recipe
            ingredients = f"Fresh ingredients for {dish_name}, oil, salt, pepper, and spices to taste"
            instructions = f"1. Prepare fresh ingredients for {dish_name}. 2. Cook according to traditional methods. 3. Season to taste. 4. Serve hot."
        
        formatted_recipe = f"""{dish_name.title()}

INGREDIENTS:
{ingredients}

INSTRUCTIONS:
{instructions}"""
        
        print(f"✅ Recipe generated successfully!")
        return formatted_recipe

    except Exception as e:
        print(f"❌ Recipe error: {e}")
        import traceback
        traceback.print_exc()
        return None


def GenerateImage(dish_name):
    try:
        print(f"🖼️ Generating image for: {dish_name}")
        # Load image generator lazily
        img_gen = load_image_generator()
        prompt = f"High quality professional food photography of {dish_name}, ultra realistic, appetizing, well-lit, on white background"
        
        image = img_gen(prompt, num_inference_steps=15, guidance_scale=7.5).images[0]
        buffered = BytesIO()
        image.save(buffered, format="PNG")
        img_str = base64.b64encode(buffered.getvalue()).decode()
        print(f"✅ Image generated successfully!")
        return img_str
    except Exception as e:
        print(f"❌ Image generation error: {e}")
        import traceback
        traceback.print_exc()
        return None

def GetRecipe(request):
    dish_name = request.GET.get("dish", "").strip()
    if not dish_name:
        return JsonResponse({"error": "Please enter a dish name."}, status=400)
    
    print(f"🔍 Requesting recipe for: {dish_name}")
    recipe = GenerateRecipe(dish_name)
    
    if not recipe:
        print(f"❌ Recipe generation failed for: {dish_name}")
        return JsonResponse({"error": f"Sorry, no recipe found for '{dish_name}'."}, status=404)
    
    # Try to generate image, but don't block on it
    image_base64 = None
    try:
        print(f"🖼️ Attempting image generation for: {dish_name}")
        image_base64 = GenerateImage(dish_name)
    except Exception as e:
        print(f"⚠️ Image generation failed (non-blocking): {e}")
        # Continue without image - recipe is more important
    
    # Return recipe immediately, image is optional
    response_data = {
        "dish": dish_name,
        "recipe": recipe,
    }
    
    if image_base64:
        response_data["image"] = image_base64
    
    print(f"✅ Returning recipe response for: {dish_name}")
    return JsonResponse(response_data)