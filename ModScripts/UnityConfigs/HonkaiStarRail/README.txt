Honkai StarRail root_vs list:
e8425f64cfb887cd    for body hair face cloth etc. but sometimes weapon also use this.
a0b21a8e787c5a98    for weapon,static object etc.
9684c4091fc9e35a    for weapon without [BLENDWEIGHTS].
Unity 2019.4 LTS use these values even between games.

Honkai StarRail Unity Version : 2019.4.34

Normally we use auto_elementlist in this game,you can use this manually at some test condition.
Possible element_list:
element_list = POSITION,NORMAL,TANGENT,COLOR,TEXCOORD,BLENDWEIGHTS,BLENDINDICES
element_list = POSITION,NORMAL,TANGENT,COLOR,TEXCOORD,TEXCOORD1,BLENDWEIGHTS,BLENDINDICES


Action Check List:
[ShaderOverride_ROOT_VS_动画VS1]
hash = e8425f64cfb887cd
if $costume_mods
  checktextureoverride = vb0
  checktextureoverride = vb2
endif

[ShaderOverride_ROOT_VS_动画VS2]
hash = 9684c4091fc9e35a
if $costume_mods
  checktextureoverride = vb0
  checktextureoverride = vb2
endif

[ShaderOverride_ROOT_VS_动画VS3]
hash = a0b21a8e787c5a98
if $costume_mods
  checktextureoverride = vb0
  checktextureoverride = vb2
endif


Test Result:
body                            pass.
weapon_with_blend               pass.
weapon_without_blend            pass.

Note:
1.If yur modify weapon item which use 9684c4091fc9e35a,you need to manually modfiy the stride of vb2 file in config file,
set it to 4 will let it work well.
2.This game sometimes use VB3 to calculate outline, so if there is a outline problem,try to set VB3 = Rssource_xxx,
and set checktextureoverride = vb3 to fix the outline problem,this happened before but not sure if it always this.
