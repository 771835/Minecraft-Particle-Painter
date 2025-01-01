import unittest
from mcpartlib.mcpartio import McParticleIO, ToMCDatapack
from mcpartlib.mcdataformat import Minecraft_Version


class TestMcParticleIO(unittest.TestCase):
    def setUp(self):
        self.filepath = 'test.mcpd'
        self.data = [{'type': 'particle', 'particle_id': 'minecraft:flame', 'pos': (0, 0, 0), 'option': [1, 2, 3]}]
        self.mc_particle_io = McParticleIO(filepath=self.filepath, data=self.data)

    def test_get_data(self):
        self.assertEqual(self.mc_particle_io.get_data(), self.data)

    def test_save_file(self):
        self.assertTrue(self.mc_particle_io.save_file())

    def test_read_file(self):
        self.mc_particle_io.save_file()
        self.mc_particle_io.data = None
        self.assertEqual(self.mc_particle_io.read_file(), self.data)

    def test_set_suffix(self):
        self.assertTrue(self.mc_particle_io.set_suffix('.test'))
        self.assertEqual(self.mc_particle_io.get_suffix(), '.test')

    def test_get_err(self):
        self.mc_particle_io.data = None
        self.mc_particle_io.filepath = None
        self.mc_particle_io.get_data()
        self.assertIsInstance(self.mc_particle_io.get_err(), FileNotFoundError)

class TestToMCDatapack(unittest.TestCase):
    def setUp(self):
        self.data = McParticleIO(data=[{'type': 'particle', 'particle_id': 'minecraft:flame', 'pos': (0, 0, 0), 'option': [1, 2, 3]}])
        self.to_mc_datapack = ToMCDatapack(data=self.data)

    def test_init(self):
        self.assertEqual(self.to_mc_datapack.data, self.data.get_data())

    def test_get_particle_command(self):
        particle_data = {'type': 'particle', 'particle_id': 'flame', 'pos': (0, 0, 0), 'option': [1, 2, 3]}
        command = self.to_mc_datapack._get_particle_command(particle_data)
        self.assertIsNotNone(command)

    def test_make_datapack(self):
        # This is a placeholder test as the method is not implemented
        self.assertIsNone(self.to_mc_datapack.make_datapack())

    def test_make_one_function_file(self):
        data = [{'type': 'particle', 'particle_id': 'flame', 'pos': (0, 0, 0), 'option': [1, 2, 3]}]
        self.to_mc_datapack._make_one_function_file(data, 'test.mcfunction')
        with open('test.mcfunction', 'r') as f:
            content = f.read()
        
        self.assertIn('particle minecraft:flame', content)

if __name__ == '__main__':
    unittest.main()
