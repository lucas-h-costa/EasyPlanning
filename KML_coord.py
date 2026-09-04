# -*- coding: utf-8 -*-

import xml.etree.ElementTree as ET
import re

def main():
    """Lê um KML e separa suas coordenadas em arquivos de pontos, linhas e polígonos."""
    # Lê o documento KML e identifica o namespace padrão.
    tree = ET.parse('input.kml')
    root = tree.getroot()
    
    # O namespace é necessário para localizar os elementos do KML.
    namespace = re.match(r'\{(.*?)\}kml', root.tag).group(1)
    ns = {'def': namespace}
    
    # Captura longitude, latitude e altitude no formato de coordenadas do KML.
    coord_ex = r'(-?\d+\.\d+),'
    heig_ex = r'(\d+)'
    regex = coord_ex + coord_ex + heig_ex
    
    # Cria os arquivos de saída, sobrescrevendo versões anteriores.
    with open('output_pins.txt','w') as out_pin,  \
         open('output_paths.txt','w') as out_pat, \
         open('output_polygons.txt','w') as out_pol:
      
        # Escreve os cabeçalhos dos arquivos de saída.
        out_pin.write('Pin Name,Latitude,Longitude,Height\n')
        out_pat.write('Pin Name,Pin_#,Latitude,Longitude,Height\n')
        out_pol.write('Pin Name,Pin_#,Latitude,Longitude,Height\n')

        # Percorre cada elemento geográfico e classifica suas coordenadas.
        for i in root.findall('.//def:Placemark', ns):
          name = i.find('def:name', ns).text
          coord = i.find('.//def:coordinates', ns)
          # Ignora elementos sem coordenadas.
          if coord is not None:
            coord = coord.text.strip()
            coord = re.findall(regex, coord)
            # Registra as coordenadas no arquivo correspondente à geometria.
            pin = 0
            for (long, lat, heig) in coord:
              pin += 1
              if i.find('.//def:Point', ns):
                out_pin.write(f'{name},{lat},{long},{heig}\n')
              elif i.find('.//def:LineString', ns):
                out_pat.write(f'{name},pin_{pin},{lat},{long},{heig}\n')
              elif i.find('.//def:Polygon', ns):
                out_pol.write(f'{name},pin_{pin},{lat},{long},{heig}\n')

if __name__ == '__main__':
    main()