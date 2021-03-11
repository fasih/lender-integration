if [ "$1" == "-f" ]; then
	echo "Start: Removing all migration files"
	find . -path "*/migrations/*.py" -not -name "__init__.py" -delete
	find . -path "*/migrations/*.pyc"  -delete
	find . -path "*/migrations/__pycache__"  -delete

	echo "Start: Removing database"
	rm *.sqlite3

	echo "Start: Running makemigrations"
	python manage.py makemigrations
fi

echo "Start: Running migrate command"
python manage.py migrate

if [ "$1" == "-f" ]; then
    echo "Start: Running initproject"
    python manage.py initproject
fi

echo "Start: Running Django HTTP Server"
python manage.py runserver --insecure 0:8000
