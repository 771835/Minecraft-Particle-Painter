import mcpartlib.mcpartio as mcio
file=mcio.McParticleIO('file.mcpd')
datapack=mcio.ToMCDatapack(file)
datapack.make_datapack()