# detections.py
# Defines the Detection class, which stores information about a detected object and all objects.

# Detection class, used to keep track of what has already been seen
class Detection(object):
	detectedLabels = set()
	
	# constructor, take name of detected object
	def __init__(self, name):
		self.name = name
		detectedLabels.add(name)

	# use the name for comparisons (hash and eq)
	def __hash__(self):
		return hash(self.name)
		
	# use the name for comparisons (hash and eq)
	def __eq__(self, other):
		return isinstance(other, DetectedObject) and self.name == other.name
