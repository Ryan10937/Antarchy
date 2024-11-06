extends Node2D

# Variables to set the icons used to represent items and creatures
@export var food: CompressedTexture2D
@export var creature_team_1: CompressedTexture2D
@export var creature_team_2: CompressedTexture2D

@export var food_count: int
@export var creature_team_1_count: int
@export var creature_team_2_count: int

# Variables to set the grid dimensions and spacing
@export var grid_width: int = 2
@export var grid_height: int = 2
@export var tilemap_spacing: float = 300  # Distance between tilemaps

# Reference to the camera
@export var camera_ref: Camera2D

# Path to the TileMap scene to instantiate
@export var tilemap_scene_path: PackedScene

# Runs when the node enters the scene tree
func _ready():
	# Call the function to spawn the grid
	spawn_tilemap_grid()
	# Adjust the camera to fit the entire grid
	position_camera()
	# Spawn food and creatures on random tiles
	place_entities()

# Function to spawn the TileMap instances in a grid
func spawn_tilemap_grid():
	# Ensure tilemap_scene_path is valid
	if tilemap_scene_path == null:
		print("Tilemap scene path is invalid!")
		return
	
	# Loop through grid width and height to place tilemaps
	for x in range(grid_width):
		for y in range(grid_height):
			# Instance a new TileMap from the scene path
			var tilemap_instance = tilemap_scene_path.instantiate()
			# Calculate the position for this tilemap based on spacing
			tilemap_instance.position = Vector2(x * tilemap_spacing, y * tilemap_spacing)
			# Add the tilemap instance to the current node
			add_child(tilemap_instance)

# Function to adjust the camera to fit the entire grid
func position_camera():
	if camera_ref == null:
		print("Camera reference is invalid!")
		return
	
	# Calculate total grid width and height based on spacing
	var total_width = (grid_width - 1) * tilemap_spacing
	var total_height = (grid_height - 1) * tilemap_spacing
	
	# Center position of the grid
	var center_position = Vector2(total_width / 2, total_height / 2)
	camera_ref.position = center_position

	# Adjust the zoom of the camera based on grid size
	var viewport_size = get_viewport_rect().size
	var zoom_x = viewport_size.x / (total_width + tilemap_spacing)
	var zoom_y = viewport_size.y / (total_height + tilemap_spacing)
	# Set the zoom to fit the entire grid
	camera_ref.zoom = Vector2(zoom_x, zoom_y)

# Function to place food and creatures on random tiles
func place_entities():
	# Get all possible positions in the grid
	var tile_positions = []
	for x in range(grid_width):
		for y in range(grid_height):
			tile_positions.append(Vector2(x * tilemap_spacing, y * tilemap_spacing))
	
	# Shuffle positions to randomize placement
	tile_positions.shuffle()
	
	# Place food entities
	for i in range(min(food_count, tile_positions.size())):
		var pos = tile_positions.pop_front()
		create_entity(food, pos)
	
	# Place team 1 creatures
	for i in range(min(creature_team_1_count, tile_positions.size())):
		var pos = tile_positions.pop_front()
		create_entity(creature_team_1, pos - Vector2(50, 0))
	
	# Place team 2 creatures
	for i in range(min(creature_team_2_count, tile_positions.size())):
		var pos = tile_positions.pop_front()
		create_entity(creature_team_2, pos + Vector2(50, 0))

# Function to create a Sprite for a given texture at a specified position
func create_entity(texture: Texture2D, tile_position: Vector2):
	var sprite = Sprite2D.new()
	sprite.texture = texture
	sprite.position = tile_position
	sprite.scale *= 3
	add_child(sprite)
