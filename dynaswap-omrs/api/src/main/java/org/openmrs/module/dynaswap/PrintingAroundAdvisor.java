package org.openmrs.module.dynaswap;

import java.lang.reflect.Method;

import org.aopalliance.aop.Advice;
import org.aopalliance.intercept.MethodInterceptor;
import org.aopalliance.intercept.MethodInvocation;
import org.springframework.aop.Advisor;
import org.springframework.aop.support.StaticMethodMatcherPointcutAdvisor;

public class PrintingAroundAdvisor extends StaticMethodMatcherPointcutAdvisor implements Advisor {
	
	public boolean matches(Method method, Class targetClass) {
		// only run on getter methods
		if (method.getName().startsWith("get"))
			return true;
		return false;
	}
	
	@Override
	public Advice getAdvice() {
		System.out.println("Getting new around advice");
		return new PrintingAroundAdvice();
	}
	
	public class PrintingAroundAdvice implements MethodInterceptor {
		
		public Object invoke(MethodInvocation invocation) throws Throwable {
			System.out.println("Before " + invocation.getMethod().getName());
			
			Object o = invocation.proceed();
			
			System.out.println("After " + invocation.getMethod().getName());
			
			return o;
		}
	}
}
