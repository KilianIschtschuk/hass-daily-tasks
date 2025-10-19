1. Install the Custom Component

Navigate to the main configuration folder of your Home Assistant installation.
This is the folder where you find configuration.yaml.

If you don't already have one, create a new folder named custom_components.

Inside custom_components, create another folder named daily_tasks.

Copy the three files (manifest.json, __init__.py, and sensor.py) into the
daily_tasks folder.

Your final folder structure should look like this:

└── config/ ├── configuration.yaml └── custom_components/ └── daily_tasks/ ├──
__init__.py ├── manifest.json └── sensor.py


2. Configure the Sensor

Now, open your configuration.yaml file and add the following lines to create the
sensor:

# configuration.yaml entry
sensor:
  - platform:
    daily_tasks name:
    "Tasks Due Today"


You can change the name to whatever you'd like.

3. Restart Home Assistant

For the changes to take effect, you need to restart Home Assistant.
You can do this by going to Settings > System > Restart.

4. Add to your Mobile Dashboard (Lovelace)

Once Home Assistant has restarted, you'll have a new entity called
sensor.tasks_due_today.
To display the tasks in a clean, mobile-friendly list, use the Markdown Card.

On your dashboard, click the three dots in the top right and select Edit
Dashboard.

Click + Add Card and choose the Markdown card.

Paste the following code into the content field:

type:
markdown title:
Tasks for Today content:
| {% set tasks = state_attr('sensor.tasks_due_today', 'tasks') %} {% if tasks
and tasks|length > 0 %} {% for task in tasks %} - **{{ task.task }}** (From:
*{{ task.list }}*) {% endfor %} {% else %} All clear for today!
✨ {% endif %}


This template will automatically update to show your tasks for the day or a
friendly completion message if there are none.
