import React, { PropTypes } from 'react';
import {Link} from 'react-router';

const NavBarIem = ({url,name,active}) => (
		<li><Link to={url}>
		 {name}
		</Link></li>


)

export default NavBarIem;


