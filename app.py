"""Preparation of files for KEGG Mapper."""

from io import StringIO

import panel as pn
pn.extension('notifications')
pn.extension(notifications=True)

def get_cid(data):
    cid = []
    for line in data.splitlines():
        ID = line.split("\t")[6]
        if ID.startswith("C"):
            cid.append(ID)
    return cid

def compute(f1_content, f2_content):

    cid1 = get_cid(f1_content)
    cid2 = get_cid(f2_content)

    # join the two lists, removing duplicates
    allcompounds = list( dict.fromkeys(cid1 + cid2))

    # transform into sets (to compute set intersection)

    set1 = set(cid1)
    set2 = set(cid2)
    both = set1.intersection(set2)
    only1 = set1.difference(both)
    only2 = set2.difference(both)
    
    results = {'n1': len(only1), 'n2': len(only2), 'n_common': len(both)}

    text = ["KEGG_ID\tcolor"]

    for compound in allcompounds:
        if compound in both:
            color = 'yellow'
        elif compound in set1:
            color = 'blue'
        else:
            color = 'red'

        text.append( f'{compound}\t{color}' )
    text = '\n'.join(text)
    results['map'] = text
    return results

# widgetry

header = pn.pane.Markdown('''## Preparation of files for KEGG Mapper

Upload two <code>.annotated</code> files generated by a <span style="color:steelblue;">
<a href="http://masstrix3.helmholtz-muenchen.de/masstrix3/" target="_blank">MassTRIX</a></span>
compound search (for different conditions, strains, etc)

This tool will generate a file, <code>map.txt</code>, in a format usable by <span style="color:steelblue;">
<a href="https://www.genome.jp/kegg/mapper.html" target="_blank">KEGG Mapper</a></span>

In <code>map.txt</code>, KeGG IDs are marked with the following colors:

- Compounds present in **both files** ➞ <span style="color:goldenrod;">yellow</span>
- Compounds present only in the **first file** ➞ <span style="color:darkblue;">blue</span>
- Compounds present only in the **second file** ➞ <span style="color:red;">red</span>

Tool developed by *António Ferreira*, *Alexandre Coelho* and *Henrique Silva*

-------''')

results = {}

file_input1 = pn.widgets.FileInput()
file_input2 = pn.widgets.FileInput()

def b_compute(event):
    out_msg.object = ''
    if file_input1.value is None and file_input2.value is None:
        out_msg.object = 'No files were selected'
        return
    if file_input1.value is None:
        out_msg.object = 'No file 1 was selected'
        return
    if file_input2.value is None:
        out_msg.object = 'No file 2 was selected'
        return
    try:
        f1_content = file_input1.value.decode('utf-8')
        f2_content = file_input2.value.decode('utf-8')
    except UnicodeDecodeError:
        f1_content = file_input1.value.decode('ISO-8859-1')
        f2_content = file_input2.value.decode('ISO-8859-1')
    name1 = file_input1.filename
    name2 = file_input2.filename

    results = compute(f1_content, f2_content)

    numbers = [f'<p>There are <span style="color:goldenrod;">{results["n_common"]}</span> common KeGG IDs in both files</p>',
            f'<p>There are <span style="color:darkblue;">{results["n1"]}</span> exclusive KeGG IDs in file <span style="color:darkblue;">{name1}</span></p>',
            f'<p>There are <span style="color:red;">{results["n2"]}</span> exclusive KeGG IDs in file <span style="color:red;">{name2}</span></p>']

    out_msg.object = '\n'.join(numbers)

    sio = StringIO()
    sio.write(results['map'])
    sio.seek(0)
    d_button = pn.widgets.FileDownload(sio, embed=True,
                                       filename='map.txt',
                                       label='Download map.txt',
                                       button_type='success',
                                       width=200)
    app_column[-1] = d_button

compute_button = pn.widgets.Button(name='Compute', width=200, button_type='primary')
compute_button.on_click(b_compute)

file_inputs = pn.Column(pn.widgets.StaticText(name='File 1', value = ' '),
                        file_input1,
                        pn.widgets.StaticText(name='File 2', value = ' '),
                        file_input2)


out_msg = pn.pane.Markdown('', width=680)
bogus_button = pn.widgets.Button(visible=False)
app_column = pn.Column(header, file_inputs, compute_button, out_msg, bogus_button, width=700)

app_column.servable()