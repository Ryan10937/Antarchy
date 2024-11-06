extends Node

var outputfile = "res://TestingText.txt"

func _ready() -> void:
	var SeenComma: bool = false
	var SeenSpace: bool = false
	var SeenF: bool = false
	var x_position: String = ""
	var y_position: String = ""
	
	if FileAccess.file_exists(outputfile) == false:
		return
		
	#create ref to the text file and open it
	var test_file = FileAccess.open(outputfile, FileAccess.READ)
	
	while not test_file.eof_reached():
		var current_string: String = test_file.get_line()
		for x in current_string.length():
			if not SeenComma:
				x_position += current_string[x]
			elif SeenComma and not SeenSpace:
				y_position += current_string[x]
		send_tile_position(x_position.to_int(), y_position.to_int())
			
	test_file.close()

func send_tile_position(x_position, y_position):
	#TODO Need to create this in the level script. Will add all the things that could be on a tile here
	#get_tree().current_scene.build_tile(x_position, y_position)
	pass
	
	
