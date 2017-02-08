import React from 'react';

import NavBar from './statics/navBar';

const Layout = (props) => (
	<div id="layout">
		<NavBar pathname={props.location.pathname}/>
		<div id="content" style={{paddingTop: 50}}>
			{props.children}
		</div>
	</div>
	)

export default Layout;