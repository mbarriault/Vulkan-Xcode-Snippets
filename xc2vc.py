from xml.etree import ElementTree as et
import glob
import re
import subprocess

def CDATA(text=None):
	element = et.Element('![CDATA[')
	element.text = text
	return element

et._original_serialize_xml = et._serialize_xml
def _serialize_xml(write, elem, qnames, namespaces, short_empty_elements, **kwargs):
	if elem.tag == '![CDATA[':
		#write("\n<%s%s]]>\n" % (elem.tag, elem.text))
		write("\n<{}{}]]>\n".format(elem.tag, elem.text))
		if elem.tail:
			write(_escape_cdata(elem.tail))
		return
	else:
		return et._original_serialize_xml(write, elem, qnames, namespaces, short_empty_elements, **kwargs)
et._serialize_xml = et._serialize['xml'] = _serialize_xml

R = re.compile(r'<#(\w+)#>')

vcroot = et.Element("CodeSnippets")
vcroot.set("xmlns", "http://schemas.microsoft.com/VisualStudio/2005/CodeSnippet")

for file in glob.glob("*.codesnippet"):
	root = et.parse(file).getroot().find("dict")
	children = list(root)
	kvs = {children[i].text : children[i+1].text for i in range(0, len(children), 2)}
	xctext = kvs["IDECodeSnippetContents"]
	kc = kvs["IDECodeSnippetCompletionPrefix"]
	name = kvs["IDECodeSnippetTitle"]
	vctext = R.sub(r'$\1$', xctext)
	
	vccodesnippet = et.SubElement(vcroot, "CodeSnippet")
	vccodesnippet.set("Format", "1.0.0")
	vcheader = et.SubElement(vccodesnippet, "Header")
	vctitle = et.SubElement(vcheader, "Title")
	vctitle.text = name
	vcshortcut = et.SubElement(vcheader, "Shortcut")
	vcshortcut.text = kc
	
	vcsnippet = et.SubElement(vccodesnippet, "Snippet")
	vccode = et.SubElement(vcsnippet, "Code")
	vccode.set("Language", "CPP")
	c = CDATA(vctext)
	vccode.append(c)
	
	vcdeclaration = et.SubElement(vcsnippet, "Declarations")
	for match in R.findall(xctext):
		vcliteral = et.SubElement(vcdeclaration, "Literal")
		vcid = et.SubElement(vcliteral, "ID")
		vcid.text = match
		vcdefault = et.SubElement(vcliteral, "Default")
		vcdefault.text = match

tree = et.ElementTree(vcroot)
tree.write("Vulkan.xml", encoding="utf-8", xml_declaration=True)
with open("Vulkan.snippet", 'w') as f:
	subprocess.call(["xmllint", "--format", "Vulkan.xml"], stdout=f)
