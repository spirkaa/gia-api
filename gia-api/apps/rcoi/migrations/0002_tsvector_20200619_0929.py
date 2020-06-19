import django.contrib.postgres.indexes
import django.contrib.postgres.search
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("rcoi", "0001_squashed_0010_auto_20200611_2046"),
    ]

    operations = [
        migrations.RunSQL(
            sql="""
            ALTER TABLE rcoi_employee
                ADD COLUMN search_vector tsvector
                    GENERATED ALWAYS AS (
                        setweight(to_tsvector(
                            'russian',
                            coalesce(name, '')
                        ), 'A')
                    ) STORED;
            CREATE INDEX rcoi_employ_search__59ec46_gin ON rcoi_employee USING gin (search_vector);
            """,
            reverse_sql="""
            ALTER TABLE rcoi_employee
                DROP COLUMN search_vector;
            """,
            state_operations=[
                migrations.AddField(
                    model_name="employee",
                    name="search_vector",
                    field=django.contrib.postgres.search.SearchVectorField(
                        blank=True, null=True
                    ),
                ),
                migrations.AddIndex(
                    model_name="employee",
                    index=django.contrib.postgres.indexes.GinIndex(
                        fields=["search_vector"], name="rcoi_employ_search__59ec46_gin"
                    ),
                ),
            ],
        ),
        migrations.RunSQL(
            sql="""
            ALTER TABLE rcoi_organisation
                ADD COLUMN search_vector tsvector
                    GENERATED ALWAYS AS (
                        setweight(to_tsvector(
                            'russian',
                            coalesce(name, '')
                        ), 'A')
                    ) STORED;
            CREATE INDEX rcoi_organi_search__216a23_gin ON rcoi_organisation USING gin (search_vector);
            """,
            reverse_sql="""
            ALTER TABLE rcoi_organisation
                DROP COLUMN search_vector;
            """,
            state_operations=[
                migrations.AddField(
                    model_name="organisation",
                    name="search_vector",
                    field=django.contrib.postgres.search.SearchVectorField(
                        blank=True, null=True
                    ),
                ),
                migrations.AddIndex(
                    model_name="organisation",
                    index=django.contrib.postgres.indexes.GinIndex(
                        fields=["search_vector"], name="rcoi_organi_search__216a23_gin"
                    ),
                ),
            ],
        ),
        migrations.RunSQL(
            sql="""
            ALTER TABLE rcoi_place
                ADD COLUMN search_vector tsvector
                    GENERATED ALWAYS AS (
                        setweight(to_tsvector('russian', coalesce(name, '')), 'A') ||
                        setweight(to_tsvector('russian', coalesce(code, '')), 'B') ||
                        setweight(to_tsvector('russian', coalesce(addr, '')), 'C')
                    ) STORED;
            CREATE INDEX rcoi_place_search__4cdf62_gin ON rcoi_place USING gin (search_vector);
            """,
            reverse_sql="""
            ALTER TABLE rcoi_place
                DROP COLUMN search_vector;
            """,
            state_operations=[
                migrations.AddField(
                    model_name="place",
                    name="search_vector",
                    field=django.contrib.postgres.search.SearchVectorField(
                        blank=True, null=True
                    ),
                ),
                migrations.AddIndex(
                    model_name="place",
                    index=django.contrib.postgres.indexes.GinIndex(
                        fields=["search_vector"], name="rcoi_place_search__4cdf62_gin"
                    ),
                ),
            ],
        ),
        migrations.RunSQL(
            sql="""
            ALTER TABLE rcoi_position
                ADD COLUMN search_vector tsvector
                    GENERATED ALWAYS AS (
                        setweight(to_tsvector(
                            'russian',
                             coalesce(name, '')
                         ), 'A')
                    ) STORED;
            CREATE INDEX rcoi_positi_search__f26330_gin ON rcoi_position USING gin (search_vector);
            """,
            reverse_sql="""
            ALTER TABLE rcoi_position
                DROP COLUMN search_vector;
            """,
            state_operations=[
                migrations.AddField(
                    model_name="position",
                    name="search_vector",
                    field=django.contrib.postgres.search.SearchVectorField(
                        blank=True, null=True
                    ),
                ),
                migrations.AddIndex(
                    model_name="position",
                    index=django.contrib.postgres.indexes.GinIndex(
                        fields=["search_vector"], name="rcoi_positi_search__f26330_gin"
                    ),
                ),
            ],
        ),
        migrations.AlterField(
            model_name="exam",
            name="datafile",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="exams",
                to="rcoi.DataFile",
            ),
        ),
        migrations.AlterModelOptions(
            name="datasource", options={"ordering": ["-modified"]},
        ),
    ]
