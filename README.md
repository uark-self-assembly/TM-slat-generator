# TM-slat-generator
Generates a set of crisscross slats that simulate a given Turing machine through self-assembly.
Assembly can be simulated using [PolyominoTAS](http://self-assembly.net/software/PolyominoTAS/) by loading the resulting .xml file.
## Getting Started
Examples of Turing machine descriptions used as input to the generator can be found in the [turing_machines](/turing_machines) directory. Turing machine descriptions can be generated using `TM_to_text.py` in the same folder.
### Generating Slats
To get help running the generator:
```bash
cd src
python TM_slat_gen.py -h
```
Typical use:
```bash
cd src
python TM_slat_gen.py -i 0100 -f example_TM.txt -o example_TM_slats.xml
```
To simulate the system, use PolyominoTAS (mentioned above) to load the generated .xml file.
