extends Node2D

# Variables to set the icons used to represent items and creatures
@export var food_texture: Texture2D
@export var creature_texture: Texture2D

# Variables to set the grid dimensions and spacing
var grid_width: int = 0
var grid_height: int = 0
var tilemap_spacing: float = 250  # Adjust as needed

# Lists to store positions of entities and food
var entity_positions: Array[Vector2] = []
var food_positions: Array[Vector2] = []

# Reference to the camera
@export var camera_ref: Camera2D

# Path to the TileMap scene to instantiate
@export var tilemap_scene_path: PackedScene

# Function to set the grid size
func set_grid_size(x_length: int, y_length: int):
	grid_width = x_length
	grid_height = y_length
	# Spawn the grid
	spawn_tilemap_grid(grid_width, grid_height)
	# Adjust the camera
	position_camera()

# Function to add an entity or food position
func add_entity(x_pos: int, y_pos: int, is_food: bool):
	if is_food:
		food_positions.append(Vector2(x_pos, y_pos))
	else:
		entity_positions.append(Vector2(x_pos, y_pos))

# Function to place all entities after data is received
func place_entities():
	# Place food entities
	for pos in food_positions:
		var tile_pos = Vector2((pos.x - 1) * tilemap_spacing, (pos.y - 1) * tilemap_spacing)
		create_entity(food_texture, tile_pos, true)
	# Place creature entities
	for pos in entity_positions:
		var tile_pos = Vector2((pos.x - 1) * tilemap_spacing, (pos.y - 1) * tilemap_spacing)
		create_entity(creature_texture, tile_pos, false)

# Function to spawn the grid (no changes made here as per your request)
func spawn_tilemap_grid(grid_width: int, grid_height: int):
	# Ensure tilemap_scene_path is valid
	if tilemap_scene_path == null:
		print("Tilemap scene path is invalid!")
		return
		
	# Your original code, unchanged
	for x in grid_width:
		for y in grid_height:
			var tilemap_instance = tilemap_scene_path.instantiate()
			tilemap_instance.position = Vector2((x - 1) * tilemap_spacing, (y - 1) * tilemap_spacing)
			add_child(tilemap_instance)

# Function to position the camera
func position_camera():
	if camera_ref == null:
		print("Camera reference is invalid!")
		return
	
	# Calculate total grid width and height based on spacing
	var total_width = grid_width  * tilemap_spacing
	var total_height = grid_height * tilemap_spacing
	
	# Center position of the grid
	var center_position = Vector2(total_width / 2, total_height / 2)
	camera_ref.position = center_position + Vector2(-500, -350)

	# Adjust the zoom of the camera based on grid size
	var viewport_size = get_viewport_rect().size
	var zoom_x = total_width / viewport_size.x
	var zoom_y = total_height / viewport_size.y
	var zoom_factor = 6.25
	camera_ref.zoom = Vector2(zoom_x / zoom_factor, zoom_y / zoom_factor)

# Function to create an entity or food sprite with proper scaling and offset
func create_entity(texture: Texture2D, tile_position: Vector2, is_food: bool):
	var sprite = Sprite2D.new()
	sprite.texture = texture
	sprite.scale *= 3  # Scale the icon to be 3 times bigger

	# Position the sprite on the tile and add any needed offset
	if is_food:
		# Center food on the tile
		sprite.position = tile_position
	else:
		# Offset entity by 50 pixels to the left from the tile's center
		sprite.position = tile_position + Vector2(-75, 0)
	
	add_child(sprite)
