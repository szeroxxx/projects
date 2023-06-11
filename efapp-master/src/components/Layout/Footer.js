import Row from "react-bootstrap/Row";
import Col from "react-bootstrap/Col";


export default function Footer(){
    const d = new Date();
    let year = d.getFullYear();
    return (
        <div className="footer">
            <Row>
                <Col md={6} sm={6} className="copyright">&copy;{year} Ennofab.com</Col>
                <Col md={6} sm={6} className="copyright d-flex flex-row-reverse"><a href={"mailto:ennofabhq@gmail.com"}>Email us</a></Col>
            </Row>    
        </div>
    )
}