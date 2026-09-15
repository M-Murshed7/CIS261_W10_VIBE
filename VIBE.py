#Mamoor Murshed
#CIS261
#Vibe Coding

"""Student records manager with test scores and letter-grade calculation."""

import csv
from dataclasses import dataclass, field
from pathlib import Path


GRADE_SCALE = (
	(90, "A"),
	(80, "B"),
	(70, "C"),
	(60, "D"),
	(0, "F"),
)
RECORD_FILE = Path("student_grades.txt")


@dataclass
class Student:
	"""Store one student's identifying information and test scores."""

	student_id: str
	name: str
	test1: float
	test2: float
	test3: float
	average: float = field(init=False)
	grade: str = field(init=False)

	def __post_init__(self) -> None:
		self.average = sum(self.scores) / 3
		self.grade = next(
			grade for minimum, grade in GRADE_SCALE if self.average >= minimum
		)

	@property
	def scores(self) -> tuple[float, float, float]:
		return self.test1, self.test2, self.test3

	@property
	def letter_grade(self) -> str:
		return self.grade


class StudentRecords:
	"""Manage students by their unique student ID."""

	def __init__(self) -> None:
		self.students: dict[str, Student] = {}

	def add_or_update(
		self, student_id: str, name: str, test1: float, test2: float, test3: float
	) -> None:
		self.students[student_id] = Student(student_id, name, test1, test2, test3)

	def remove(self, student_id: str) -> bool:
		return self.students.pop(student_id, None) is not None

	def ordered_students(self) -> list[Student]:
		return sorted(self.students.values(), key=lambda student: student.name.lower())

	def find_by_name(self, name: str) -> list[Student]:
		search_name = name.casefold()
		return [
			student
			for student in self.ordered_students()
			if search_name in student.name.casefold()
		]

	def save(self, filename: Path = RECORD_FILE) -> None:
		with filename.open("w", newline="", encoding="utf-8") as file:
			writer = csv.writer(file, delimiter="|")
			writer.writerow(("name", "id", "test1", "test2", "test3", "average", "grade"))
			for student in self.ordered_students():
				writer.writerow(
					(
						student.name,
						student.student_id,
						*(f"{score:.2f}" for score in student.scores),
						f"{student.average:.2f}",
						student.grade,
					)
				)

	def load(self, filename: Path = RECORD_FILE) -> int:
		if not filename.exists():
			return 0
		loaded = 0
		with filename.open(newline="", encoding="utf-8") as file:
			reader = csv.DictReader(file, delimiter="|")
			for row in reader:
				try:
					name = row["name"].strip()
					student_id = row["id"].strip()
					if not student_id or not name:
						continue
					self.add_or_update(
						student_id,
						name,
						float(row["test1"]),
						float(row["test2"]),
						float(row["test3"]),
					)
					loaded += 1
				except (KeyError, TypeError, ValueError):
					continue
		return loaded


def read_score(prompt: str) -> float:
	while True:
		try:
			score = float(input(prompt))
			if 0 <= score <= 100:
				return score
		except ValueError:
			pass
		print("Enter a score from 0 to 100.")


def save_records(records: StudentRecords) -> bool:
	try:
		records.save()
	except (OSError, csv.Error) as error:
		print(f"Could not save records to {RECORD_FILE}: {error}")
		return False
	return True


def load_records(records: StudentRecords) -> int:
	try:
		return records.load()
	except (OSError, csv.Error) as error:
		print(f"Could not load records from {RECORD_FILE}: {error}")
		return 0


def add_student(records: StudentRecords) -> bool:
	student_id = input("Student ID: ").strip()
	name = input("Student name: ").strip()
	if not student_id or not name:
		print("Student ID and name are required.")
		return False
	test1 = read_score("Test 1 score: ")
	test2 = read_score("Test 2 score: ")
	test3 = read_score("Test 3 score: ")
	records.add_or_update(student_id, name, test1, test2, test3)
	print(f"Student record added for {name}. Average: {records.students[student_id].average:.2f}, "
		f"Grade: {records.students[student_id].grade}")
	return True


def print_student(student: Student) -> None:
	scores = ", ".join(f"{score:.2f}" for score in student.scores)
	print(
		f"{student.student_id:<12} {student.name:<24} {scores:<24} "
		f"{student.average:>7.2f}  {student.letter_grade}"
	)


def display_students(records: StudentRecords) -> None:
	if not records.students:
		print("No student records found.")
		return
	print(f"{'ID':<12} {'Name':<24} {'Scores':<24} {'Average':>7}  Grade")
	print("-" * 78)
	for student in records.ordered_students():
		print_student(student)


def display_student_record(records: StudentRecords) -> None:
	student_id = input("Enter student ID: ").strip()
	student = records.students.get(student_id)
	if student is None:
		print(f"No student record found for ID {student_id}.")
		return
	print("\nStudent Record")
	print(f"Name: {student.name}")
	print(f"ID: {student.student_id}")
	print(f"Test 1: {student.test1:.2f}")
	print(f"Test 2: {student.test2:.2f}")
	print(f"Test 3: {student.test3:.2f}")
	print(f"Average: {student.average:.2f}")
	print(f"Grade: {student.grade}")


def display_summary(records: StudentRecords) -> None:
	if not records.students:
		print("No student records found.")
		return
	students = records.ordered_students()
	class_average = sum(student.average for student in students) / len(students)
	highest = max(students, key=lambda student: student.average)
	lowest = min(students, key=lambda student: student.average)
	print(f"Highest average: {highest.average:.2f} ({highest.name})")
	print(f"Lowest average: {lowest.average:.2f} ({lowest.name})")
	print(f"Class average: {class_average:.2f}")


def display_search_results(students: list[Student]) -> None:
	if not students:
		print("No students matched that name.")
		return
	print(f"{'ID':<12} {'Name':<24} {'Scores':<24} {'Average':>7}  Grade")
	print("-" * 78)
	for student in students:
		print_student(student)


def run() -> None:
	records = StudentRecords()
	loaded = load_records(records)
	if loaded:
		print(f"Loaded {loaded} student record(s) from {RECORD_FILE}.")
	actions = {
		"1": "Add or update student",
		"2": "View all students",
		"3": "View class statistics",
		"4": "Search by name",
		"5": "View student record",
		"6": "Save and exit",
	}

	while True:
		print("\nStudent Records Manager")
		for number, label in actions.items():
			print(f"{number}. {label}")
		try:
			choice = input("Choose an option (press ESC to exit): ")
		except (EOFError, KeyboardInterrupt):
			choice = "\x1b"
		if choice.strip() == "\x1b" or choice == "\x1b":
			if save_records(records):
				print(f"Records saved to {RECORD_FILE}. Goodbye.")
			return
		choice = choice.strip()

		if choice == "1":
			if add_student(records):
				save_records(records)
		elif choice == "2":
			display_students(records)
		elif choice == "3":
			display_summary(records)
		elif choice == "4":
			name = input("Name to search for: ").strip()
			display_search_results(records.find_by_name(name))
		elif choice == "5":
			display_student_record(records)
		elif choice == "6":
			if save_records(records):
				print(f"Records saved to {RECORD_FILE}. Goodbye.")
			return
		else:
			print("Choose an option from 1 to 5.")


if __name__ == "__main__":
	run()