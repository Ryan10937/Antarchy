extends Node

var outputfile = "res://Logs/state_at_06_12_34_33_908725.json"
var grid_x_length: int
var grid_y_length: int

var visualization_script_instance

func _ready() -> void:
	# set the visualization script
	visualization_script_instance = get_tree().current_scene
	process_next_file()

# Function to process the JSON file and handle grid size, entities, and food
func process_next_file():
	var file = FileAccess.open(outputfile, FileAccess.READ)
	if file:
		# Read the entire file content as text
		var file_content = file.get_as_text()
		file.close()  # Close the file after reading

		# Create an instance of JSON and parse the content
		var json_parser = JSON.new()
		var error = json_parser.parse(file_content)
		if error == OK:
			var json_data = json_parser.data
			# Process grid size
			get_grid_size(json_data)
			# Process entities and food
			process_entities(json_data)
			process_food(json_data)
			# After all entities are added, call place_entities
			visualization_script_instance.place_entities()
		else:
			# Print an error message if parsing fails
			print("Failed to parse JSON: ", json_parser.get_error_message())
	else:
		print("Could not open file: ", outputfile)

# Function to extract and send the grid size
func get_grid_size(json_data):
	if json_data.has("grid_size"):
		grid_x_length = json_data["grid_size"][0]
		grid_y_length = json_data["grid_size"][1]
		send_grid_size(grid_x_length, grid_y_length)

# Function to process and send each entity's position if it is alive
func process_entities(json_data):
	if json_data.has("entities"):
		for entity in json_data["entities"]:
			if entity.has("is_alive") and entity["is_alive"] == true:
				var position = entity["position"]
				var x_pos = position[0]
				var y_pos = position[1]
				send_new_entity(x_pos, y_pos, false)

# Function to process and send each food item's position
func process_food(json_data):
	if json_data.has("food"):
		for food in json_data["food"]:
			if food.has("is_alive") and food["is_alive"] == true:
				var position = food["position"]
				var x_pos = position[0]
				var y_pos = position[1]
				send_new_entity(x_pos, y_pos, true)

# Function to send grid size
func send_grid_size(x_length, y_length):
	# Call the visualization script's set_grid_size method
	visualization_script_instance.set_grid_size(x_length, y_length)

# Function to send entity or food positions
func send_new_entity(x_pos, y_pos, is_food: bool):
	visualization_script_instance.add_entity(x_pos, y_pos, is_food)
