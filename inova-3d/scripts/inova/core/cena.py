"""Gestao de colecoes e primitivas geometricas.

Toda a cena fica sob a colecao raiz "INOVA". Cada modulo constroi dentro da
sua propria subcolecao e chama `colecao_limpa` antes, o que torna os scripts
reexecutaveis: rodar de novo apaga e recria apenas aquela parte, sem duplicar
objetos nem deixar malhas orfas.
"""
import math

import bmesh
import bpy
from mathutils import Matrix, Vector

RAIZ_CENA = "INOVA"


def colecao(caminho):
    """Obtem (ou cria) colecoes aninhadas a partir de 'A/B/C'."""
    pai = bpy.context.scene.collection
    for nome in [RAIZ_CENA] + [p for p in caminho.split("/") if p]:
        col = bpy.data.collections.get(nome)
        if col is None:
            col = bpy.data.collections.new(nome)
        if col.name not in pai.children:
            pai.children.link(col)
        pai = col
    return pai


def _apagar_conteudo(col):
    for filho in list(col.children):
        _apagar_conteudo(filho)
        bpy.data.collections.remove(filho)
    for obj in list(col.objects):
        dados = obj.data
        bpy.data.objects.remove(obj, do_unlink=True)
        if dados is not None and dados.users == 0:
            if isinstance(dados, bpy.types.Mesh):
                bpy.data.meshes.remove(dados)
            elif isinstance(dados, bpy.types.Curve):
                bpy.data.curves.remove(dados)
            elif isinstance(dados, bpy.types.Camera):
                bpy.data.cameras.remove(dados)
            elif isinstance(dados, bpy.types.Light):
                bpy.data.lights.remove(dados)


def colecao_limpa(caminho):
    col = colecao(caminho)
    _apagar_conteudo(col)
    return col


def purgar_orfaos():
    for bloco in (bpy.data.meshes, bpy.data.curves, bpy.data.materials, bpy.data.images, bpy.data.node_groups):
        for item in list(bloco):
            if item.users == 0:
                bloco.remove(item)


def _vincular(obj, col, mat):
    col.objects.link(obj)
    if mat is not None:
        if isinstance(mat, (list, tuple)):
            for m in mat:
                obj.data.materials.append(m)
        else:
            obj.data.materials.append(mat)
    return obj


def _uv_caixa(bm):
    """UV em metros por projecao no eixo dominante de cada face."""
    uv = bm.loops.layers.uv.verify()
    for f in bm.faces:
        n = f.normal
        eixo = max(range(3), key=lambda i: abs(n[i]))
        for loop in f.loops:
            co = loop.vert.co
            if eixo == 0:
                loop[uv].uv = (co.y, co.z)
            elif eixo == 1:
                loop[uv].uv = (co.x, co.z)
            else:
                loop[uv].uv = (co.x, co.y)


def objeto_bmesh(nome, col, bm, mat=None, origem=None):
    me = bpy.data.meshes.new(nome)
    _uv_caixa(bm)
    bm.to_mesh(me)
    bm.free()
    obj = bpy.data.objects.new(nome, me)
    if origem is not None:
        obj.location = origem
    return _vincular(obj, col, mat)


def caixa(nome, col, x0, x1, y0, y1, z0, z1, mat=None, chanfro=0.0):
    """Caixa alinhada aos eixos, com vertices em coordenadas de mundo."""
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    for v in bm.verts:
        v.co = Vector((
            x0 + (v.co.x + 0.5) * (x1 - x0),
            y0 + (v.co.y + 0.5) * (y1 - y0),
            z0 + (v.co.z + 0.5) * (z1 - z0),
        ))
    obj = objeto_bmesh(nome, col, bm, mat)
    if chanfro > 0:
        mod = obj.modifiers.new("chanfro", "BEVEL")
        mod.width = chanfro
        mod.segments = 2
        mod.limit_method = "ANGLE"
    return obj


def caixa_local(nome, col, dx, dy, dz, mat=None, centro=(0, 0, 0), chanfro=0.0):
    """Caixa centrada em `centro` (coordenadas locais), para pecas de objetos moveis."""
    cx, cy, cz = centro
    return caixa(nome, col, cx - dx / 2, cx + dx / 2, cy - dy / 2, cy + dy / 2, cz - dz / 2, cz + dz / 2, mat, chanfro)


def prisma(nome, col, contorno, z0, z1, mat=None):
    """Extruda um poligono XY (lista de (x, y) em sentido anti-horario) entre z0 e z1."""
    bm = bmesh.new()
    base = [bm.verts.new((x, y, z0)) for x, y in contorno]
    topo = [bm.verts.new((x, y, z1)) for x, y in contorno]
    bm.faces.new(list(reversed(base)))
    bm.faces.new(topo)
    n = len(contorno)
    for i in range(n):
        j = (i + 1) % n
        bm.faces.new((base[i], base[j], topo[j], topo[i]))
    bm.normal_update()
    return objeto_bmesh(nome, col, bm, mat)


def plano_uv(nome, col, cantos, mat=None):
    """Quadrilatero com UV 0..1 (cantos: inf-esq, inf-dir, sup-dir, sup-esq)."""
    me = bpy.data.meshes.new(nome)
    me.from_pydata([tuple(c) for c in cantos], [], [(0, 1, 2, 3)])
    uv = me.uv_layers.new(name="UVMap")
    for i, co in enumerate(((0, 0), (1, 0), (1, 1), (0, 1))):
        uv.data[i].uv = co
    obj = bpy.data.objects.new(nome, me)
    return _vincular(obj, col, mat)


def cilindro(nome, col, x, y, z0, raio, altura, mat=None, lados=32, eixo="Z", liso=True):
    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=True, segments=lados, radius1=raio, radius2=raio, depth=altura)
    if eixo == "X":
        bmesh.ops.rotate(bm, verts=bm.verts, cent=(0, 0, 0), matrix=Matrix.Rotation(math.pi / 2, 3, "Y"))
    elif eixo == "Y":
        bmesh.ops.rotate(bm, verts=bm.verts, cent=(0, 0, 0), matrix=Matrix.Rotation(math.pi / 2, 3, "X"))
    desloc = Vector((x, y, z0 + (altura / 2 if eixo == "Z" else 0)))
    bmesh.ops.translate(bm, verts=bm.verts, vec=desloc)
    obj = objeto_bmesh(nome, col, bm, mat)
    if liso:
        for p in obj.data.polygons:
            p.use_smooth = len(p.vertices) == 4
    return obj


def juntar(nome, objetos):
    """Une varios objetos em um so (reduz contagem de objetos em elementos repetidos)."""
    if not objetos:
        return None
    alvo = objetos[0]
    ctx = {"active_object": alvo, "selected_editable_objects": objetos, "object": alvo}
    with bpy.context.temp_override(**ctx):
        bpy.ops.object.join()
    alvo.name = nome
    alvo.data.name = nome
    return alvo


def instanciar(nome, col, origem_col, local, rot_z_graus=0.0, escala=1.0):
    """Instancia uma colecao-modelo (veiculos, motos) sem duplicar malhas."""
    emp = bpy.data.objects.new(nome, None)
    emp.instance_type = "COLLECTION"
    emp.instance_collection = origem_col
    emp.location = local
    emp.rotation_euler = (0, 0, math.radians(rot_z_graus))
    emp.scale = (escala, escala, escala)
    col.objects.link(emp)
    return emp
