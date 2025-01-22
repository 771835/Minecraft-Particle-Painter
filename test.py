import mcpartlib.mcpartio as mcio
file=mcio.McParticleIO('a.mcpd')
datapack=mcio.ToMCDatapack(file)
datapack.make_datapack()
file.close()