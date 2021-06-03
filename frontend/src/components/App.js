import React, { Component } from "react";
import { render } from "react-dom";
import {
  Card, CardImg, CardText, CardBody,
  CardTitle, CardSubtitle, Button
} from 'reactstrap';


class App extends Component {
  constructor(props) {
    super(props);
    this.state = {elements :[],curr_page:1,has_previous:false,has_next:true}
    this.handlePageChange(this.state.curr_page)
  }

  async handlePageChange(page_number){

    var data = new FormData();
    data.append("page_number", page_number);

    const opt = {
      method:"POST",
      body: data
    }
    let elements = []

    const art_data = await fetch('get_article_data/',opt)
    const art_res = await art_data.json()


    for(let i=0;i<art_res.id.length;i++){
      const det_data = await fetch(`article_api/${art_res.id[i]}/`)
      const det_res = await det_data.json()
      elements.push(det_res)

    }
    this.setState({
      has_previous:art_res.has_previous,
      has_next:art_res.has_next,
      total:art_res.total,
      elements:elements,
      curr_page:page_number
    })

  }

  render() {

    if(this.state.elements.length > 1){
    return (
      <div id="card_div">
        <Card className="text-white bg-info">
          <CardTitle className="text-center mt-3" style={{fontSize:"1.2em",fontFamily:'"Comic Sans MS", cursive, sans-serif'}}>Top rated documents</CardTitle>
          <CardBody className="bg-light text-dark most_viewed">
            <div className="row">
              {this.state.elements.map(article => {
                let url = `article/${article.pk}/`
                return (
                   <div className="col-12 my-2 border-bottom d-flex" key={article.pk}>
                     <p>{article.title}</p>
                     <a href={url} className="ml-auto mr-2">&#8594;</a>
                   </div>
                  );
              })}
            </div>
        <nav aria-label="Page navigation example" className="d-flex">
          <ul className="pagination mx-auto">
              {(()=>{if(this.state.has_previous){
                  return (
                    <>
                    <li className="page-item"><a className="page-link" onClick={()=>this.handlePageChange(1)} href="#"><span aria-hidden="true">&laquo;</span></a></li>
                    <li className="page-item"><a className="page-link" onClick={()=>this.handlePageChange(this.state.curr_page-1)} href="#"><span aria-hidden="true">&lt;</span></a></li>
                    </>
                  )}
                  else{
                    return (
                      <>
                      <li className="page-item disabled"><a className="page-link" tabIndex="-1" href="#"><span aria-hidden="true">&laquo;</span></a></li>
                      <li className="page-item disabled"><a className="page-link" tabIndex="-1" href="#"><span aria-hidden="true">&lt;</span></a></li>
                      </>
                    )
                  }
              })()}
              {(()=>{if(this.state.curr_page-1>=1){
                return (<li className="page-item"><a className="page-link" onClick={()=>this.handlePageChange(this.state.curr_page-1)} href="#"><span aria-hidden="true">{this.state.curr_page-1}</span></a></li>)
              }})()}
              <li className="page-item active"><a className="page-link" href="#">{this.state.curr_page}</a></li>
              {(()=>{if(this.state.curr_page+1<=this.state.total){
                return (<li className="page-item"><a className="page-link" onClick={()=>this.handlePageChange(this.state.curr_page+1)} href="#"><span aria-hidden="true">{this.state.curr_page+1}</span></a></li>)
              }})()}

              {(()=>{if(this.state.has_next){
                  return (
                    <>
                    <li className="page-item"><a className="page-link" onClick={()=>this.handlePageChange(this.state.curr_page+1)} href="#"><span aria-hidden="true">&gt;</span></a></li>
                    <li className="page-item"><a className="page-link" onClick={()=>this.handlePageChange(this.state.total)} href="#"><span aria-hidden="true">&raquo;</span></a></li>
                    </>
                  )}
                  else{
                    return (
                      <>
                      <li className="page-item disabled"><a className="page-link" tabIndex="-1" href="#"><span aria-hidden="true">&gt;</span></a></li>
                      <li className="page-item disabled"><a className="page-link" tabIndex="-1" href="#"><span aria-hidden="true">&raquo;</span></a></li>
                      </>
                    )
                  }
                })()}
                </ul>
          </nav>
          </CardBody>
        </Card>
      </div>
    );
    }
    else{
      return (<></>)
    }
  }
}

export default App;

const container = document.getElementById("app");
render(<App />, container);
