	.file	"profile-handle-pointer-v1.c"
	.text
	.p2align 2,,3
.globl _typed_entry
	.def	_typed_entry;	.scl	2;	.type	32;	.endef
_typed_entry:
	pushl	%ebp
	movl	%esp, %ebp
	subl	$8, %esp
	movl	12(%ebp), %eax
	sall	$5, %eax
	addl	8(%ebp), %eax
	movl	%eax, 12(%ebp)
	movl	16(%ebp), %eax
	movl	%eax, 8(%ebp)
	leave
	jmp	_stricmp
	.p2align 2,,3
.globl _byte_entry
	.def	_byte_entry;	.scl	2;	.type	32;	.endef
_byte_entry:
	pushl	%ebp
	movl	%esp, %ebp
	subl	$8, %esp
	movl	12(%ebp), %eax
	sall	$5, %eax
	addl	8(%ebp), %eax
	movl	%eax, 12(%ebp)
	movl	16(%ebp), %eax
	movl	%eax, 8(%ebp)
	leave
	jmp	_stricmp
	.p2align 2,,3
.globl _typed_current
	.def	_typed_current;	.scl	2;	.type	32;	.endef
_typed_current:
	pushl	%ebp
	movl	%esp, %ebp
	subl	$8, %esp
	movl	12(%ebp), %eax
	movl	8(%ebp), %edx
	addl	$6, %edx
	movl	%edx, 12(%ebp)
	movl	%eax, 8(%ebp)
	leave
	jmp	_stricmp
	.p2align 2,,3
.globl _byte_current
	.def	_byte_current;	.scl	2;	.type	32;	.endef
_byte_current:
	pushl	%ebp
	movl	%esp, %ebp
	subl	$8, %esp
	movl	12(%ebp), %eax
	movl	8(%ebp), %edx
	addl	$6, %edx
	movl	%edx, 12(%ebp)
	movl	%eax, 8(%ebp)
	leave
	jmp	_stricmp
	.def	_stricmp;	.scl	2;	.type	32;	.endef
