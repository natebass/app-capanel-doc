import { defineConfig } from '@pandacss/dev'
import chakraPreset from '@chakra-ui/panda-preset'

export default defineConfig({
  //... other config
  preflight: false, // Disables the reset
  presets: [chakraPreset],
  outdir: 'styled-system',
  //... other config
})
