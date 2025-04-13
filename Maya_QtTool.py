from maya import cmds
import os
import re
from PySide6 import QtWidgets
from PySide6.QtUiTools import QUiLoader
from maya.app.general.mayaMixin import MayaQWidgetBaseMixin

# 絶対パスで設定 ※可能なら相対パスで処理できるようにしたい。
UIFILEPATH = r"F:\3D\Maya_dev\SBT_Qt2.ui"

class Simple_Bind_Tool(MayaQWidgetBaseMixin, QtWidgets.QMainWindow):
    def __init__(self, *args, **kwargs):
        super(Simple_Bind_Tool, self).__init__(*args, **kwargs)

        self.widget = QUiLoader().load(UIFILEPATH)
        self.setWindowTitle("Simple_Bind_Tool")
        self.setCentralWidget(self.widget)

        self.scene = QtWidgets.QGraphicsScene()
        self.widget.log.setScene(self.scene)
        self.log_text = QtWidgets.QGraphicsTextItem()
        self.scene.addItem(self.log_text)

        self.widget.bind_body_btn.clicked.connect(self.select_sets_bodyonly)
        self.widget.bind_bodySK_btn.clicked.connect(self.select_sets_bodySK)
        self.widget.bind_bodysailor_btn.clicked.connect(self.select_sets_bodysailor)
        self.widget.bind_all_btn.clicked.connect(self.select_sets_all)
        self.widget.bindskin_btn.clicked.connect(self.bind_skin_function)
        self.widget.unbind_btn.clicked.connect(self.unbind_skin_function)
        self.widget.copyskin_obj.clicked.connect(self.copyskin_function)
        self.widget.copyskin_obj_2.clicked.connect(self.copyskin_function)
        self.widget.copyskin_ver.clicked.connect(self.copyskin_function)
        self.widget.bind_copy_btn.clicked.connect(self.bind_copy_function)
        self.widget.delete_history_btn.clicked.connect(self.delete_history_function)
        self.widget.delete_history_btn_2.clicked.connect(self.delete_history_function)
        self.widget.remove_influence_btn.clicked.connect(self.remove_influence_function)
        self.widget.remove_influence_btn_2.clicked.connect(self.remove_influence_function)
        self.widget.hair_bind_btn.clicked.connect(self.hair_bind_function)
        self.widget.create_linobj_btn.clicked.connect(self.create_line_obj)
        self.widget.vertex_btn.clicked.connect(self.create_line_obj)

        self.logs = []

    def log_message(self, message):
        self.logs.append(message)
        log_text = "\n".join(self.logs)
        self.log_text.setPlainText(log_text)
        new_height = self.log_text.boundingRect().height()
        self.scene.setSceneRect(0, 0, self.widget.log.width(), max(new_height, self.widget.log.height()))

        self.log_text.setPos(0, 0)
        self.widget.log.ensureVisible(self.log_text)

    """--------- 要素設定 ---------"""
    def select_obj_add_list(self): #選択オブジェクトをリスト追加
        select_obj = []
        selection = cmds.ls(selection=True)
        if selection:
            select_obj.extend(selection)
            print(f"selected_obj: {select_obj}")
        else:
            self.log_message("NO")
        return select_obj

    def select_sets_list(self,set_name): #setの内容取得
        bind_joint = []
        if cmds.objExists(set_name):
            set_elements = cmds.sets(set_name, q=True)
            if set_elements:
                bind_joint.extend(set_elements)
        else:
            self.log_message("No set elements")
        return bind_joint

    def bind_setting(self, bind_sets_joint, select_obj): #バインドの設定
        if not bind_sets_joint:
            self.log_message("Error: No joints provided for binding.")
            return
        if not select_obj:
            self.log_message("Error: No objects selected for binding.")
            return
        for bind_obj in select_obj:
            if cmds.objExists(bind_obj):
                cmds.skinCluster(bind_sets_joint, bind_obj, tsb=True, mi=4)
                self.log_message("Skin binding completed successfully.")
            else:
                self.log_message(f"Error: Object {bind_obj} does not exist.")

    def obj_copyweight_setting(self):  # コピーウェイト（オブジェクト・頂点）
        selection = cmds.ls(selection=True, flatten=True)

        if len(selection) != 2:
            self.log_message("Select two objects or vertices (source → target)")
            return

        # 頂点選択かオブジェクト選択か判定
        source_is_vertex = ".vtx[" in selection[0]
        target_is_vertex = ".vtx[" in selection[1]

        if source_is_vertex and target_is_vertex:
            # 両方とも頂点の場合
            source_mesh = selection[0].split(".vtx[")[0]
            target_mesh = selection[1].split(".vtx[")[0]
            source_verts = [selection[0]]
            target_verts = [selection[1]]
        elif not source_is_vertex and not target_is_vertex:
            # 両方ともオブジェクトの場合
            source_mesh, target_mesh = selection
            source_verts = None
            target_verts = None
        else:
            self.log_message("Select either two objects or two corresponding vertices")
            return

        # SkinCluster の取得
        try:
            source_skin_cluster = cmds.ls(cmds.listHistory(source_mesh), type="skinCluster")[0]
            target_skin_cluster = cmds.ls(cmds.listHistory(target_mesh), type="skinCluster")[0]
        except IndexError:
            self.log_message("The selected object has no skin cluster")
            return

        try:
            if source_verts and target_verts:
                # 頂点単位でウェイトをコピー
                cmds.copySkinWeights(
                    sourceSkin=source_skin_cluster,
                    destinationSkin=target_skin_cluster,
                    noMirror=True,
                    surfaceAssociation="closestPoint",
                    influenceAssociation="closestJoint",
                    sourceInfluence=source_verts,
                    destinationInfluence=target_verts
                )
                self.log_message(f"Skin weight copied from {source_verts} to {target_verts}.")
            else:
                # オブジェクト単位でウェイトをコピー
                cmds.copySkinWeights(
                    sourceSkin=source_skin_cluster,
                    destinationSkin=target_skin_cluster,
                    noMirror=True,
                    surfaceAssociation="closestPoint",
                    influenceAssociation="closestJoint"
                )
                self.log_message(f"Skin weight copied from {source_mesh} to {target_mesh}.")
        except Exception as e:
            self.log_message(f"Error: {str(e)}")

    def bind_and_copyweight(self):
        selection = cmds.ls(selection = True)
        if len(selection) != 2:
            self.log_message("Select two objects(source mesh → bind mesh）")
            return
        source_mesh, bind_mesh = selection
        self.log_message(bind_mesh)
        source = cmds.listHistory(source_mesh, pdo= True)
        skin = cmds.ls(source, typ= "skinCluster")

        if not skin:
            self.log_message("The first object to be selected is object with skinCluster.")
            return

        if self.widget.bind_body_btn.isChecked():
            bind_sets_joint = self.select_sets_bodyonly()

        elif self.widget.bind_bodySK_btn.isChecked():
            bind_sets_joint = self.select_sets_bodySK()

        elif self.widget.bind_bodysailor_btn.isChecked():
            bind_sets_joint = self.select_sets_bodysailor()

        elif self.widget.bind_all_btn.isChecked():
            bind_sets_joint = self.select_sets_all()

        else:
            self.log_message("Error: No set selection made.")
            return

        if not bind_sets_joint:
            self.log_message("Error: No joints selected for binding.")
            return
        bind_obj = cmds.ls(bind_mesh)
        self.bind_setting(bind_sets_joint, bind_obj)

        try:
            source_skin_cluster = cmds.ls(cmds.listHistory(source_mesh), type='skinCluster')[0]
            target_skin_cluster = cmds.ls(cmds.listHistory(bind_mesh), type='skinCluster')[0]
        except IndexError:
            self.log_message("The selected object has no skin cluster")
            return

        try:
            cmds.copySkinWeights(
                sourceSkin=source_skin_cluster,
                destinationSkin=target_skin_cluster,
                noMirror=True,
                surfaceAssociation='closestPoint',
                influenceAssociation='closestJoint'
            )
            self.log_message(f"skinweight {source_mesh} to {bind_mesh} copy.")
        except Exception as e:
            self.log_message(f"Error: {str(e)}")

        pass

    def get_root_node(self,node):
        """
        指定ノードの最上位の親（ルートノード）を取得
        """
        parent = cmds.listRelatives(node, parent=True, fullPath=True)
        if parent:
            return self.get_root_node(parent[0])  # 再帰的に親を探す
        return node  # 最上位のノードを返す

    def get_joints_in_hierarchy(self,node):
        """
        指定ノードの階層内にある Joint（ジョイント）のみを再帰的に取得
        """
        joints = []
        children = cmds.listRelatives(node, children=True, fullPath=True) or []  # フルパスで子ノードを取得

        for child in children:
            if cmds.nodeType(child) == "joint":  # Joint の場合のみ追加
                joints.append(child)
            joints.extend(self.get_joints_in_hierarchy(child))  # 再帰的に子ノードを探索
        return joints

    def hair_bind_setting(self,selected):
        if selected:
            root_nodes = set()  # 重複を防ぐためセットを使用
            for obj in selected:
                root_nodes.add(self.get_root_node(obj))  # 最上位の親（ルートノード）を取得

            all_joints = []
            for root in root_nodes:
                all_joints.extend(self.get_joints_in_hierarchy(root))  # ルートから探索
            filtered = [j for j in all_joints if "_s" not in j.split('|')[-1]]
            all_joints = filtered  # フィルタリングされたジョイントを使う
            self.bind_setting(all_joints, selected)

    def trancefer_vertex(self):
        selected = cmds.ls(selection=True, flatten=True)
        if len(selected) != 2:
            self.log_message("Select two objects or vertices (source → target)")
            return
        source_mesh, target_mesh = selected
        


    """--------- ボタン機能 ---------"""
    def select_sets_bodyonly(self):
        set_name = "body"
        bind_sets_joint = self.select_sets_list(set_name)
        print("Sets body only selected")
        return bind_sets_joint

    def select_sets_bodySK(self):
        bind_sets_joint = []
        set_name_body = "body"
        set_name_sk = "sk"
        body = self.select_sets_list(set_name_body)
        sk = self.select_sets_list(set_name_sk)
        bind_sets_joint = body + sk
        print("Sets body and sk selected")
        return bind_sets_joint

    def select_sets_bodysailor(self):
        bind_sets_joint = []
        set_name_body = "body"
        set_name_sailor = "sailor"
        body = self.select_sets_list(set_name_body)
        sailor = self.select_sets_list(set_name_sailor)
        bind_sets_joint = body + sailor
        print("Sets body and sailor selected")
        return bind_sets_joint

    def select_sets_all(self):
        bind_sets_joint = []
        set_name_body = "body"
        set_name_sailor = "sailor"
        set_name_sk = "sk"
        body = self.select_sets_list(set_name_body)
        sailor = self.select_sets_list(set_name_sailor)
        sk = self.select_sets_list(set_name_sk)
        bind_sets_joint = body + sailor + sk
        print("Sets body sailor and sk selected")
        return bind_sets_joint

    def bind_skin_function(self):
        if self.widget.bind_body_btn.isChecked():
            bind_sets_joint = self.select_sets_bodyonly()

        elif self.widget.bind_bodySK_btn.isChecked():
            bind_sets_joint = self.select_sets_bodySK()

        elif self.widget.bind_bodysailor_btn.isChecked():
            bind_sets_joint = self.select_sets_bodysailor()

        elif self.widget.bind_all_btn.isChecked():
            bind_sets_joint = self.select_sets_all()

        else:
            self.log_message("Error: No set selection made.")
            return

        if not bind_sets_joint:
            self.log_message("Error: No joints selected for binding.")
            return

        bind_obj = self.select_obj_add_list()

        if not bind_obj:
            self.log_message("Error: No objects selected for binding.")
            return
        self.bind_setting(bind_sets_joint, bind_obj)

    def unbind_skin_function(self):
        selected_objects = cmds.ls(selection=True)
        if not selected_objects:
            self.log_message("No objects selected.")
            return
        for obj in selected_objects:
            cmds.delete(obj, ch = True)
            self.log_message(f"{selected_objects}: unbind object/delete history")

    def copyskin_function(self): #未完成
        self.obj_copyweight_setting()


    def bind_copy_function(self):
        self.bind_and_copyweight()

    def delete_history_function(self):
        select_objects = cmds.ls(selection = True)
        for obj in select_objects:
            cmds.bakePartialHistory(obj, prePostDeformers=True)
        self.log_message(f"{select_objects}: delete nondeformer history")

    def remove_influence_function(self):
        select_objects = cmds.ls(selection=True)

        if not select_objects:
            self.log_message("No objects selected.")
            return

        for obj in select_objects:
            skin_clusters = cmds.ls(cmds.listHistory(obj), type='skinCluster')

            if not skin_clusters:
                self.log_message(f"No skin cluster found on: {obj}")
                continue

            skin_cluster = skin_clusters[0]

            # 削除前のインフルエンス数
            before_influences = cmds.skinCluster(skin_cluster, query=True, influence=True)
            before_count = len(before_influences)

            # 不要なインフルエンスを削除
            cmds.skinCluster(skin_cluster, edit=True, removeUnusedInfluence=True)

            # 削除後のインフルエンス数
            after_influences = cmds.skinCluster(skin_cluster, query=True, influence=True)
            after_count = len(after_influences)

            # 削除されたインフルエンス数
            removed_count = before_count - after_count

            self.log_message(f"{obj}: before {before_count}  → after {after_count}  （{removed_count} influence deleted.）")

    def export_obj_function(self):
        export_obj = self.select_obj_add_list()

        self.log_message("Export Objects")

    def hair_bind_function(self,selected):
        selected = cmds.ls(selection=True, long=True)  # `long=True` でフルパス取得
        self.hair_bind_setting(selected)

    def create_line_obj(self):
        selected = cmds.ls(sl=True, o=True, fl=True)
        if selected:
            base_name = selected[0].split("|")[-1]  # 最後の部分を取得
            new_name = base_name + "_line"
            duplicate_obj = cmds.duplicate(selected[0], name=new_name)  # 複製
            cmds.polySoftEdge(duplicate_obj[0], angle=180)
            cmds.delete(duplicate_obj[0], ch=True)  # 履歴を削除
            line_obj = cmds.ls(duplicate_obj[0])
            self.hair_bind_setting(line_obj)  # バインド設定

            source_skin_cluster = cmds.ls(cmds.listHistory(selected[0]), type="skinCluster")[0]
            target_skin_cluster = cmds.ls(cmds.listHistory(line_obj[0]), type="skinCluster")[0]
            cmds.copySkinWeights(
                sourceSkin=source_skin_cluster,
                destinationSkin=target_skin_cluster,
                noMirror=True,
                surfaceAssociation="closestPoint",
                influenceAssociation="closestJoint"
            )
        else:
            self.log_message("No object selected for line creation.")
        self.log_message("Line object created and bound successfully.")

def main():
    window = Simple_Bind_Tool()
    window.show()

if __name__ == '__main__':
    main()
