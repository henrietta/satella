=====================
Configuration sources
=====================

At the core of your config files, there are Sources. A Source is a single source of configuration - it could be
an environment variable, or a particular file, or a directory full of these files.

.. autoclass:: satella.configuration.sources.StaticSource
    :members:

.. autoclass:: satella.configuration.sources.StaticSource
    :members:

.. autoclass:: satella.configuration.sources.EnvironmentSource
    :members:

.. autoclass:: satella.configuration.sources.EnvVarsSource
    :members:

.. autoclass:: satella.configuration.sources.FileSource
    :members:

.. autoclass:: satella.configuration.sources.DirectorySource
    :members:


Then there are abstract sources of configuration.

.. autoclass:: satella.configuration.sources.AlternativeSource
    :members:

.. autoclass:: satella.configuration.sources.OptionalSource
    :members:

.. autoclass:: satella.configuration.sources.MergingSource
    :members:

In order to actually load the configuration, use the method ``provide()``.

Note that `FileSource` will try parsing the file with any modules, available, so if you
want parsing for **yaml** and **toml**, you better install `pyyaml` and `toml` respectively.

Note that JSON will be parsed using `ujson` if the module is available.

JSON schema
===========

The JSON schema consists of defining particular sources, embedded in one another.

::

    {
        "type": "ClassNameOfTheSource",
        "args": [
        ],
        "kwarg_1": ...,
        "kwarg_2": ...,
    }

If an argument consists of a dict with ``type`` key, it will be also loaded and passed internally as a source.
One of three reserved types is ``lambda``, which expects to have a key of ``operation``. This will be appended to
``lambda x: `` and ``eval()``-uated.

Always you can provide a key called ``optional`` with a value of True, this will wrap given Source in OptionalSource.

The second reserved type if ``binary``. This will encode the ``value`` key with ``encoding`` encoding (default is ascii).

The third reserved type is ``import``. It imports an expression and calls it with
discovered value, returning the output.

It accepts the following variables:

* module - module to import the expression from
* attribute - name of the attribute inside the module
* cast_before - a type to convert the value to before applying it to.

Eg:

::

    class MyEnum(enum.IntEnum):
        A = 0

    os.environ['TEST_ENV'] = '2'

    dct = {
        "type": "EnvironmentSource",
        "args": ["TEST_ENV", "TEST_ENV"],
        "cast_to": {
            "module": "my_module",
            "attribute": "MyEnum",
            "cast_before": {
                "type": "lambda",
                "operation": "int"
            }
        }
    }

    config = load_source_from_dict(dct)
    assert config.provide()['TEST_ENV'] == MyEnum(0)

To instantiate the schema, use the following functions:

.. autofunction:: satella.configuration.sources.load_source_from_dict

.. autofunction:: satella.configuration.sources.load_source_from_list

Please note that if your attacker has control over these files, he might
provoke the application into executing arbitrary Python, so
remember to **sanitize your inputs!**
