public class GFG { 
  
    // create a local interface with one abstract 
    // method run() 
    interface myInterface { 
        void run(); 
    } 
  
    // function have implements another function run() 
    static void Foo() 
    { 
        // implement run method inside Foo() function 
        myInterface r = new myInterface() { 
            public void run() 
            { 
                System.out.println("geeksforgeeks"); 
            }; 
        }; 
        r.run(); 
    } 
    public static void main(String[] args) 
    { 
        Foo(); 
    } 
} 
