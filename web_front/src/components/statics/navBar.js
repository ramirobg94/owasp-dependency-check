import React, {Component, PropTypes } from 'react';
import {Link} from 'react-router';

import NavBarIem from './navBarItem';

class NavBar extends Component {
  
  constructor(props){
    super(props)
  }

  render(){

    console.log(this.props.pathname)
    const pathname = this.props.pathname.substring(1);

    return(
      <div id="navBar" className="navbar navbar-default">
      <div className="container-fluid">
        <div className="navbar-header">
          <a className="navbar-brand" href="/">WebSiteName</a>
        </div>
      <ul className="nav navbar-nav navbar-right">

        <NavBarIem url='/' name='home' active={pathname == ''}/>

      </ul>
        
      </div>
      </div>
    )
  }

}

export default NavBar;