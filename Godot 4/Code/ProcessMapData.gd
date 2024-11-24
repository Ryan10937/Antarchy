extends Node

var grid_x_length: int
var grid_y_length: int
var visualization_script_instance

var directory_path: String  # Will be set in _ready()
var wait_time: float = 0.5  # Declare wait_time

func _ready() -> void:
	var executable_path = OS.get_executable_path()
	var executable_dir = executable_path.get_base_dir()
	directory_path = executable_dir + "/Logs/"
	
	ensure_directory_exists()
	visualization_script_instance = get_tree().current_scene
	process_files()

func ensure_directory_exists():
	if not DirAccess.dir_exists_absolute(directory_path):
		var err = DirAccess.make_dir_recursive_absolute(directory_path)
		if err != OK and err != ERR_ALREADY_EXISTS:
			print("Failed to create directory: %s, Error Code: %s" % [directory_path, err])

func is_valid_file_name(file_name: String) -> bool:
	var expected_extension = ".json"
	if not file_name.ends_with(expected_extension):
		return false
	var parts = file_name.split("_")
	return parts.size() >= 6

func extract_timestamp(file_name: String) -> int:
	var parts = file_name.split("_")
	if parts.size() < 6:
		print("Invalid filename format: %s" % file_name)
		return 0
	return int(parts[2] + parts[3] + parts[4] + parts[5])

func process_files() -> void:
	while true:
		var dir = DirAccess.open(directory_path)
		if dir:
			var files = []
			dir.list_dir_begin()
			var file_name = dir.get_next()
			while file_name != "":
				if !dir.current_is_dir():
					if is_valid_file_name(file_name):
						files.append(file_name)
				file_name = dir.get_next()
			dir.list_dir_end()

			if files.size() > 0:
				# Sort files by timestamps
				files.sort_custom(func(a, b):
					var a_timestamp = extract_timestamp(a)
					var b_timestamp = extract_timestamp(b)
					return a_timestamp < b_timestamp
				)

				# Process the oldest file based on timestamp
				var oldest_file = files[0]
				var file_path = directory_path + "/" + oldest_file
				var file = FileAccess.open(file_path, FileAccess.READ)

				if file:
					# Read the entire file content
					var file_content = file.get_as_text()
					file.close()

					# Remove the processed file
					var err = DirAccess.remove_absolute(file_path)
					if err != OK:
						print("Failed to delete file: %s, Error Code: %s" % [oldest_file, err])

					# Clear the screen and data before loading new file data
					visualization_script_instance.clear_screen()

					# Process the file content
					process_next_file(file_content)
				else:
					print("Failed to open file: %s" % oldest_file)
			else:
				print("No valid files found. Waiting for %s seconds." % wait_time)
		else:
			print("Failed to open directory: %s" % directory_path)
		
		await get_tree().create_timer(wait_time).timeout

func process_next_file(file_content):
	# Clear previous data to avoid duplication
	visualization_script_instance.entity_positions.clear()
	visualization_script_instance.food_positions.clear()
	
	# Create an instance of JSON and parse the content
	var json_parser = JSON.new()
	var error = json_parser.parse(file_content)
	if error == OK:
		var json_data = json_parser.data
		get_grid_size(json_data)
		process_entities(json_data)
		process_food(json_data)
		visualization_script_instance.place_entities()
	else:
		print("Failed to parse JSON: ", json_parser.get_error_message())

func get_grid_size(json_data):
	if json_data.has("grid_size"):
		grid_x_length = json_data["grid_size"][0]
		grid_y_length = json_data["grid_size"][1]
		send_grid_size(grid_x_length, grid_y_length)

func process_entities(json_data):
	if json_data.has("entities"):
		for entity in json_data["entities"]:
			if entity.has("is_alive") and entity["is_alive"] == true:
				var position = entity["position"]
				var x_pos = position[0]
				var y_pos = position[1]
				send_new_entity(x_pos, y_pos, false)

func process_food(json_data):
	if json_data.has("food"):
		for food in json_data["food"]:
			if food.has("is_alive") and food["is_alive"] == true:
				var position = food["position"]
				var x_pos = position[0]
				var y_pos = position[1]
				send_new_entity(x_pos, y_pos, true)

func send_grid_size(x_length, y_length):
	visualization_script_instance.set_grid_size(x_length, y_length)

func send_new_entity(x_pos, y_pos, is_food: bool):
	visualization_script_instance.add_entity(x_pos, y_pos, is_food)
