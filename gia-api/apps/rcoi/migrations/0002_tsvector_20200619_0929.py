import django.contrib.postgres.indexes
import django.contrib.postgres.search
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("rcoi", "0001_squashed_0010_auto_20200611_2046"),
    ]

    operations = [
        migrations.AddField(
            model_name="employee",
            name="search_vector",
            field=django.contrib.postgres.search.SearchVectorField(
                blank=True, null=True
            ),
        ),
        migrations.AddField(
            model_name="organisation",
            name="search_vector",
            field=django.contrib.postgres.search.SearchVectorField(
                blank=True, null=True
            ),
        ),
        migrations.AddField(
            model_name="place",
            name="search_vector",
            field=django.contrib.postgres.search.SearchVectorField(
                blank=True, null=True
            ),
        ),
        migrations.AddField(
            model_name="position",
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
        migrations.AddIndex(
            model_name="organisation",
            index=django.contrib.postgres.indexes.GinIndex(
                fields=["search_vector"], name="rcoi_organi_search__216a23_gin"
            ),
        ),
        migrations.AddIndex(
            model_name="place",
            index=django.contrib.postgres.indexes.GinIndex(
                fields=["search_vector"], name="rcoi_place_search__4cdf62_gin"
            ),
        ),
        migrations.AddIndex(
            model_name="position",
            index=django.contrib.postgres.indexes.GinIndex(
                fields=["search_vector"], name="rcoi_positi_search__f26330_gin"
            ),
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
            name="datasource",
            options={"ordering": ["-modified"]},
        ),
        migrations.RunSQL(
            sql="""
            CREATE FUNCTION tsv_place_trigger() RETURNS trigger AS $$
            begin
                new.search_vector :=
                    setweight(to_tsvector('pg_catalog.russian', coalesce(new.code, '')), 'B') ||
                    setweight(to_tsvector('pg_catalog.russian', coalesce(new.name, '')), 'C') ||
                    setweight(to_tsvector('pg_catalog.russian', coalesce(new.addr, '')), 'D');
                return new;
            end
            $$ LANGUAGE plpgsql;

            CREATE TRIGGER search_vector_update BEFORE INSERT OR UPDATE
                ON rcoi_place FOR EACH ROW EXECUTE FUNCTION tsv_place_trigger();

            UPDATE rcoi_place SET id = id;
            """,
            reverse_sql="""
            DROP TRIGGER search_vector_update ON rcoi_place;
            DROP FUNCTION tsv_place_trigger;
            """,
        ),
        migrations.RunSQL(
            sql="""
            CREATE FUNCTION tsv_name_a_trigger() RETURNS trigger AS $$
            begin
                new.search_vector :=
                    setweight(to_tsvector('pg_catalog.russian', coalesce(new.name, '')), 'A');
                return new;
            end
            $$ LANGUAGE plpgsql;

            CREATE TRIGGER search_vector_update BEFORE INSERT OR UPDATE
                ON rcoi_employee FOR EACH ROW EXECUTE FUNCTION tsv_name_a_trigger();

            UPDATE rcoi_employee SET id = id;
            """,
            reverse_sql="""
            DROP TRIGGER search_vector_update ON rcoi_employee;
            DROP FUNCTION tsv_name_a_trigger;
            """,
        ),
        migrations.RunSQL(
            sql="""
            CREATE FUNCTION tsv_name_b_trigger() RETURNS trigger AS $$
            begin
                new.search_vector :=
                    setweight(to_tsvector('pg_catalog.russian', coalesce(new.name, '')), 'B');
                return new;
            end
            $$ LANGUAGE plpgsql;

            CREATE TRIGGER search_vector_update BEFORE INSERT OR UPDATE
                ON rcoi_organisation FOR EACH ROW EXECUTE FUNCTION tsv_name_b_trigger();
            UPDATE rcoi_organisation SET id = id;
            """,
            reverse_sql="""
            DROP TRIGGER search_vector_update ON rcoi_organisation;
            DROP FUNCTION tsv_name_b_trigger;
            """,
        ),
        migrations.RunSQL(
            sql="""
            CREATE FUNCTION tsv_name_c_trigger() RETURNS trigger AS $$
            begin
                new.search_vector :=
                    setweight(to_tsvector('pg_catalog.russian', coalesce(new.name, '')), 'C');
                return new;
            end
            $$ LANGUAGE plpgsql;

            CREATE TRIGGER search_vector_update BEFORE INSERT OR UPDATE
                ON rcoi_position FOR EACH ROW EXECUTE FUNCTION tsv_name_c_trigger();

            UPDATE rcoi_position SET id = id;
            """,
            reverse_sql="""
            DROP TRIGGER search_vector_update ON rcoi_position;
            DROP FUNCTION tsv_name_c_trigger;
            """,
        ),
    ]
