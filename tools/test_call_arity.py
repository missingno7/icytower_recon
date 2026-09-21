import unittest
from call_arity import conflicts


class CallArityTests(unittest.TestCase):
    def expected(self,n=4,variadic=False):return {'parameter_types':['int']*n,'variadic':variadic}
    def test_real_style_surplus_arguments_identifies_caller(self):
        text='int my_alert(char*,char*,int,int); void handle_menu(){my_alert("handle_menu",buf,NULL,"OK",NULL,0,0);}'
        rows=conflicts(text,'my_alert',self.expected())
        self.assertEqual(len(rows),1);self.assertEqual(rows[0]['caller'],'handle_menu')
        self.assertEqual(rows[0]['observed_argument_groups'],7)
        self.assertEqual(rows[0]['arguments'][0],'"handle_menu"')

    def test_literals_nested_calls_arrays_and_comments_do_not_split_arguments(self):
        text='void f(){ my_alert("a,b", nested(1,2), (int[]){1,2}, /* , ) */ 0); }'
        self.assertEqual(conflicts(text,'my_alert',self.expected()),[])
        self.assertEqual(conflicts('void f(){my_alert("hello");}','my_alert',self.expected(1)),[])
        self.assertEqual(conflicts('void f(){my_alert(/* none */);}','my_alert',self.expected(0)),[])

    def test_variadic_minimum_and_unrelated_declarations_members_are_respected(self):
        self.assertEqual(conflicts('void f(){my_alert(1,2,3);}','my_alert',self.expected(2,True)),[])
        self.assertEqual(len(conflicts('void f(){my_alert(1);}','my_alert',self.expected(2,True))),1)
        self.assertEqual(conflicts('int my_alert(int); void f(){x.my_alert(1); p->my_alert(1);}','my_alert',self.expected()),[])


if __name__=='__main__':unittest.main()
