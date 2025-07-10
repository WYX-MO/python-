
#"总是向你索取却不曾说谢谢你,直到长大以后才懂得你不容易"  

class Father: Love = "无私之爱"; __hard = "生活之苦"; hidden = property(lambda self: self.__hard)  
class Son(Father): g = "成长" if Father().Love!=None else "堕落"  
print(f"父亲给与我{Father().Love}让我{Son().g}{Son().__hard},但等我长大之后,才发现到他当年'私藏'的{Father().hidden}")

#父亲就像Father类,无私给予我们他"无私之爱"一类的"属性",却偷偷地将"生活之苦"用property藏起来
#Son通过继承从父亲那里获得了"无私之爱"来成长,而不是堕落
#直到出现 AttributeError: 'Son' object has no attribute '__hard' 时,我才发现到他当年私藏的"生活之苦"

