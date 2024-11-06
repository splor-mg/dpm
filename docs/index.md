# Data Package Manager (dpm)

**Description**: {{ project_description }}

**Version**: {{ project_version }}

**Dependencies**:

{% for dependency in dependencies %}
- {{ dependency | format_dependency }}
{% endfor %}
