from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED
root=Path(__file__).resolve().parents[1]
files=[root/'SKILL.md',root/'LICENSE']
for directory in ['scripts','references','templates','agents']:
    files += [p for p in (root/directory).rglob('*') if p.is_file() and '__pycache__' not in p.parts]
with ZipFile(root/'dist/whoownswhat.zip','w',ZIP_DEFLATED) as z:
    for p in sorted(files):z.write(p,Path('whoownswhat')/p.relative_to(root))
portable='''# WhoOwnsWhat — portable chat instructions

Paste this entire document into a new conversation, or attach it and ask the assistant to follow it. Attach your existing project records to resume. This prompt does not install a tool or connect an account.

If this host has no file or code tools, use chat-only mode: produce the complete updated record for the user to save. Never claim it was saved outside this conversation. The Python helper mentioned below is in the repository / skill ZIP; do not claim you ran it if it is not available. The local and MCP references and notes template are included below; read them here rather than trying to open their original relative paths.

'''
for name in ['SKILL.md','references/local.md','references/mcp.md','templates/project-notes.md']:
    content=(root/name).read_text()
    if name=='SKILL.md':content=content.split('---',2)[2].strip()
    portable+='\n\n---\n\n'+content
(root/'dist/CHATGPT.md').write_text(portable+'\n')
with ZipFile(root/'dist/whoownswhat.zip') as z:
    assert z.testzip() is None
    assert 'whoownswhat/SKILL.md' in z.namelist()
    assert not any('__pycache__' in p for p in z.namelist())
print('Packaged',len(files),'skill files;', (root/'dist/whoownswhat.zip').stat().st_size,'bytes')
