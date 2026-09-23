
docs/attempts/research-luna-profile-interface/build/profile-interface-late-header-v1/unit.o:     file format pe-i386


Disassembly of section .text:

0000089c <_profile_data_page_advanced>:
     89c:	55                   	push   %ebp
     89d:	89 e5                	mov    %esp,%ebp
     89f:	57                   	push   %edi
     8a0:	56                   	push   %esi
     8a1:	53                   	push   %ebx
     8a2:	83 ec 3c             	sub    $0x3c,%esp
     8a5:	8b 5d 08             	mov    0x8(%ebp),%ebx
     8a8:	c7 04 24 00 08 00 00 	movl   $0x800,(%esp)
     8af:	e8 00 00 00 00       	call   8b4 <_profile_data_page_advanced+0x18>
     8b4:	89 c6                	mov    %eax,%esi
     8b6:	c6 00 00             	movb   $0x0,(%eax)
     8b9:	bf 01 00 00 00       	mov    $0x1,%edi
     8be:	8b 84 bb 84 00 00 00 	mov    0x84(%ebx,%edi,4),%eax
     8c5:	85 c0                	test   %eax,%eax
     8c7:	7e 1c                	jle    8e5 <_profile_data_page_advanced+0x49>
     8c9:	89 44 24 10          	mov    %eax,0x10(%esp)
     8cd:	89 7c 24 0c          	mov    %edi,0xc(%esp)
     8d1:	89 74 24 08          	mov    %esi,0x8(%esp)
     8d5:	c7 44 24 04 af 00 00 	movl   $0xaf,0x4(%esp)
     8dc:	00 
     8dd:	89 34 24             	mov    %esi,(%esp)
     8e0:	e8 00 00 00 00       	call   8e5 <_profile_data_page_advanced+0x49>
     8e5:	47                   	inc    %edi
     8e6:	83 ff 06             	cmp    $0x6,%edi
     8e9:	75 d3                	jne    8be <_profile_data_page_advanced+0x22>
     8eb:	8b 83 88 00 00 00    	mov    0x88(%ebx),%eax
     8f1:	85 c0                	test   %eax,%eax
     8f3:	7e 1a                	jle    90f <_profile_data_page_advanced+0x73>
     8f5:	89 74 24 08          	mov    %esi,0x8(%esp)
     8f9:	c7 44 24 04 cb 00 00 	movl   $0xcb,0x4(%esp)
     900:	00 
     901:	89 34 24             	mov    %esi,(%esp)
     904:	e8 00 00 00 00       	call   909 <_profile_data_page_advanced+0x6d>
     909:	8b 83 88 00 00 00    	mov    0x88(%ebx),%eax
     90f:	bf 01 00 00 00       	mov    $0x1,%edi
     914:	85 c0                	test   %eax,%eax
     916:	7e 46                	jle    95e <_profile_data_page_advanced+0xc2>
     918:	8b 44 bb 5c          	mov    0x5c(%ebx,%edi,4),%eax
     91c:	89 45 e4             	mov    %eax,-0x1c(%ebp)
     91f:	85 c0                	test   %eax,%eax
     921:	7e 3b                	jle    95e <_profile_data_page_advanced+0xc2>
     923:	8b 44 bb 70          	mov    0x70(%ebx,%edi,4),%eax
     927:	99                   	cltd
     928:	f7 7d e4             	idivl  -0x1c(%ebp)
     92b:	89 44 24 10          	mov    %eax,0x10(%esp)
     92f:	89 7c 24 0c          	mov    %edi,0xc(%esp)
     933:	89 74 24 08          	mov    %esi,0x8(%esp)
     937:	c7 44 24 04 cf 00 00 	movl   $0xcf,0x4(%esp)
     93e:	00 
     93f:	89 34 24             	mov    %esi,(%esp)
     942:	89 7d e0             	mov    %edi,-0x20(%ebp)
     945:	e8 00 00 00 00       	call   94a <_profile_data_page_advanced+0xae>
     94a:	8b 4d e0             	mov    -0x20(%ebp),%ecx
     94d:	47                   	inc    %edi
     94e:	83 ff 06             	cmp    $0x6,%edi
     951:	74 13                	je     966 <_profile_data_page_advanced+0xca>
     953:	8b 84 8b 88 00 00 00 	mov    0x88(%ebx,%ecx,4),%eax
     95a:	85 c0                	test   %eax,%eax
     95c:	7f ba                	jg     918 <_profile_data_page_advanced+0x7c>
     95e:	89 f9                	mov    %edi,%ecx
     960:	47                   	inc    %edi
     961:	83 ff 06             	cmp    $0x6,%edi
     964:	75 ed                	jne    953 <_profile_data_page_advanced+0xb7>
     966:	8b 7b 74             	mov    0x74(%ebx),%edi
     969:	85 ff                	test   %edi,%edi
     96b:	7e 14                	jle    981 <_profile_data_page_advanced+0xe5>
     96d:	89 74 24 08          	mov    %esi,0x8(%esp)
     971:	c7 44 24 04 cb 00 00 	movl   $0xcb,0x4(%esp)
     978:	00 
     979:	89 34 24             	mov    %esi,(%esp)
     97c:	e8 00 00 00 00       	call   981 <_profile_data_page_advanced+0xe5>
     981:	c7 45 e4 00 00 00 00 	movl   $0x0,-0x1c(%ebp)
     988:	31 ff                	xor    %edi,%edi
     98a:	66 90                	xchg   %ax,%ax
     98c:	8b 84 bb b0 00 00 00 	mov    0xb0(%ebx,%edi,4),%eax
     993:	85 c0                	test   %eax,%eax
     995:	7e 26                	jle    9bd <_profile_data_page_advanced+0x121>
     997:	89 44 24 10          	mov    %eax,0x10(%esp)
     99b:	8b 04 bd 60 01 00 00 	mov    0x160(,%edi,4),%eax
     9a2:	89 44 24 0c          	mov    %eax,0xc(%esp)
     9a6:	89 74 24 08          	mov    %esi,0x8(%esp)
     9aa:	c7 44 24 04 eb 00 00 	movl   $0xeb,0x4(%esp)
     9b1:	00 
     9b2:	89 34 24             	mov    %esi,(%esp)
     9b5:	e8 00 00 00 00       	call   9ba <_profile_data_page_advanced+0x11e>
     9ba:	ff 45 e4             	incl   -0x1c(%ebp)
     9bd:	47                   	inc    %edi
     9be:	83 ff 0a             	cmp    $0xa,%edi
     9c1:	75 c9                	jne    98c <_profile_data_page_advanced+0xf0>
     9c3:	8b 4d e4             	mov    -0x1c(%ebp),%ecx
     9c6:	85 c9                	test   %ecx,%ecx
     9c8:	74 14                	je     9de <_profile_data_page_advanced+0x142>
     9ca:	89 74 24 08          	mov    %esi,0x8(%esp)
     9ce:	c7 44 24 04 cb 00 00 	movl   $0xcb,0x4(%esp)
     9d5:	00 
     9d6:	89 34 24             	mov    %esi,(%esp)
     9d9:	e8 00 00 00 00       	call   9de <_profile_data_page_advanced+0x142>
     9de:	89 f0                	mov    %esi,%eax
     9e0:	83 c4 3c             	add    $0x3c,%esp
     9e3:	5b                   	pop    %ebx
     9e4:	5e                   	pop    %esi
     9e5:	5f                   	pop    %edi
     9e6:	c9                   	leave
     9e7:	c3                   	ret
